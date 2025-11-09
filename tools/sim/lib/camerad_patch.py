"""
Patch for camerad.py to add pure Python RGB to YUV conversion fallback
when OpenCL is not available or fails to compile kernels.
"""

import numpy as np

def rgb_to_yuv_numpy(rgb):
    """
    Convert RGB to NV12 YUV format using pure NumPy.
    This is slower than OpenCL but works without GPU/OpenCL support.
    """
    assert rgb.dtype == np.uint8
    H, W = rgb.shape[:2]

    # RGB to YUV conversion matrix (BT.601)
    r = rgb[:, :, 0].astype(np.float32)
    g = rgb[:, :, 1].astype(np.float32)
    b = rgb[:, :, 2].astype(np.float32)

    # Y channel
    y = (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)

    # Downsample for UV
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

    # Flatten to bytes
    y_bytes = y.tobytes()
    uv_bytes = uv.tobytes()

    return y_bytes + uv_bytes
