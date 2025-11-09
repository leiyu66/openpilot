import numpy as np
import os
import pyopencl as cl
import pyopencl.array as cl_array

from msgq.visionipc import VisionIpcServer, VisionStreamType
from cereal import messaging

from openpilot.common.basedir import BASEDIR
from openpilot.tools.sim.lib.common import W, H

class Camerad:
  """Simulates the camerad daemon"""
  def __init__(self, dual_camera):
    self.pm = messaging.PubMaster(['roadCameraState', 'wideRoadCameraState'])

    self.frame_road_id = 0
    self.frame_wide_id = 0
    self.vipc_server = VisionIpcServer("camerad")

    self.vipc_server.create_buffers(VisionStreamType.VISION_STREAM_ROAD, 5, W, H)
    if dual_camera:
      self.vipc_server.create_buffers(VisionStreamType.VISION_STREAM_WIDE_ROAD, 5, W, H)

    self.vipc_server.start_listener()

    # set up for pyopencl rgb to yuv conversion
    self.use_opencl = False
    try:
      self.ctx = cl.create_some_context(interactive=False)
      self.queue = cl.CommandQueue(self.ctx)
      cl_arg = f" -DHEIGHT={H} -DWIDTH={W} -DRGB_STRIDE={W * 3} -DUV_WIDTH={W // 2} -DUV_HEIGHT={H // 2} -DRGB_SIZE={W * H} -DCL_DEBUG "

      kernel_fn = os.path.join(BASEDIR, "tools/sim/rgb_to_nv12.cl")
      with open(kernel_fn) as f:
        prg = cl.Program(self.ctx, f.read()).build(cl_arg)
        self.krnl = prg.rgb_to_nv12
      self.Wdiv4 = W // 4 if (W % 4 == 0) else (W + (4 - W % 4)) // 4
      self.Hdiv4 = H // 4 if (H % 4 == 0) else (H + (4 - H % 4)) // 4
      self.use_opencl = True
      print("[INFO] Using OpenCL for RGB to YUV conversion")
    except Exception as e:
      print(f"[WARNING] OpenCL initialization failed: {e}")
      print("[INFO] Falling back to NumPy RGB to YUV conversion (slower but compatible)")

  def cam_send_yuv_road(self, yuv):
    self._send_yuv(yuv, self.frame_road_id, 'roadCameraState', VisionStreamType.VISION_STREAM_ROAD)
    self.frame_road_id += 1

  def cam_send_yuv_wide_road(self, yuv):
    self._send_yuv(yuv, self.frame_wide_id, 'wideRoadCameraState', VisionStreamType.VISION_STREAM_WIDE_ROAD)
    self.frame_wide_id += 1

  # Returns: yuv bytes
  def rgb_to_yuv(self, rgb):
    assert rgb.shape == (H, W, 3), f"{rgb.shape}"
    assert rgb.dtype == np.uint8

    if self.use_opencl:
      rgb_cl = cl_array.to_device(self.queue, rgb)
      yuv_cl = cl_array.empty_like(rgb_cl)
      self.krnl(self.queue, (self.Wdiv4, self.Hdiv4), None, rgb_cl.data, yuv_cl.data).wait()
      yuv = np.resize(yuv_cl.get(), rgb.size // 2)
      return yuv.data.tobytes()
    else:
      # NumPy fallback for RGB to NV12 YUV conversion
      r = rgb[:, :, 0].astype(np.float32)
      g = rgb[:, :, 1].astype(np.float32)
      b = rgb[:, :, 2].astype(np.float32)

      # Y channel (full resolution)
      y = (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)

      # Downsample for UV (half resolution)
      r_down = r[::2, ::2]
      g_down = g[::2, ::2]
      b_down = b[::2, ::2]

      # U and V channels
      u = (-0.169 * r_down - 0.331 * g_down + 0.500 * b_down + 128).clip(0, 255).astype(np.uint8)
      v = (0.500 * r_down - 0.419 * g_down - 0.081 * b_down + 128).clip(0, 255).astype(np.uint8)

      # Interleave U and V for NV12 format
      uv = np.empty((H // 2, W // 2, 2), dtype=np.uint8)
      uv[:, :, 0] = u
      uv[:, :, 1] = v

      return y.tobytes() + uv.tobytes()

  def _send_yuv(self, yuv, frame_id, pub_type, yuv_type):
    eof = int(frame_id * 0.05 * 1e9)
    self.vipc_server.send(yuv_type, yuv, frame_id, eof, eof)

    dat = messaging.new_message(pub_type, valid=True)
    msg = {
      "frameId": frame_id,
      "transform": [1.0, 0.0, 0.0,
                    0.0, 1.0, 0.0,
                    0.0, 0.0, 1.0]
    }
    setattr(dat, pub_type, msg)
    self.pm.send(pub_type, dat)
