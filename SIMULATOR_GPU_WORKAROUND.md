# OpenPilot Simulator GPU/OpenCL Workaround

## Problem
When running openpilot simulator in a devcontainer, `modeld` (the vision model process) fails to start due to OpenCL initialization errors:

```
python3: common/clutil.cc:60: cl_device_id cl_get_device_id(cl_device_type): Assertion `CL_SUCCESS == (clGetPlatformIDs(0, __null, &num_platforms))' failed.
```

This occurs because:
1. OpenCL drivers may not be properly configured in the container
2. Even with NVIDIA GPU passthrough (`--gpus all`), OpenCL ICD (Installable Client Driver) registration may fail
3. The container's OpenCL environment doesn't match the host driver version

## Impact
Without `modeld` running:
- No `cameraOdometry` messages are published
- `locationd` waits for `cameraOdometry` and sets `posenetOK=False`
- Cruise control engagement (`press '2'`) is blocked with "⏳ System initializing" message
- The simulator cannot be used for testing

## Solution
Since `modeld` is not strictly required in simulator mode (the simulator generates its own camera frames), we implemented a workaround by having the simulator bridge publish fake `cameraOdometry` messages directly.

### Changes Made

#### 1. Modified `tools/sim/lib/simulated_sensors.py`
- Added `'cameraOdometry'` to the PubMaster list
- Added `send_fake_camera_odometry()` method to publish stable fake odometry data
- Integrated fake odometry publishing into the `update()` loop at 20 Hz

```python
def send_fake_camera_odometry(self, simulator_state: 'SimulatorState'):
    """Send fake cameraOdometry messages when modeld is not running (GPU unavailable)"""
    dat = messaging.new_message('cameraOdometry', valid=True)
    # Provide stable fake odometry data
    dat.cameraOdometry.trans = [0.0, 0.0, 0.0]
    dat.cameraOdometry.rot = [0.0, 0.0, 0.0]
    dat.cameraOdometry.transStd = [0.1, 0.1, 0.1]
    dat.cameraOdometry.rotStd = [0.01, 0.01, 0.01]
    self.pm.send('cameraOdometry', dat)
```

#### 2. Updated `.devcontainer/devcontainer.json`
Added `postStartCommand` to attempt OpenCL ICD registration (for cases where it might work):

```json
"postStartCommand": "sudo mkdir -p /etc/OpenCL/vendors && echo 'libnvidia-opencl.so.1' | sudo tee /etc/OpenCL/vendors/nvidia.icd > /dev/null || true"
```

Note: This command includes `|| true` so it won't fail container startup if OpenCL registration doesn't work.

## Testing
To verify the fix works:

1. Start openpilot:
   ```bash
   ./tools/sim/launch_openpilot.sh
   ```

2. Start bridge:
   ```bash
   ./tools/sim/run_bridge.py
   ```

3. Test cameraOdometry messages:
   ```bash
   python3 test_camera_od.py
   ```

Expected output:
```
✓ Received cameraOdometry message! Frame 0
  trans: [0, 0, 0]
  rot: [0, 0, 0]
  alive: True
```

4. In the bridge window, press `2` to engage cruise control after the warmup period completes

## Limitations
- This workaround provides static fake odometry data, which is sufficient for basic simulator testing but may not accurately reflect real camera motion
- For production testing or more realistic simulations, proper OpenCL/GPU support would be required to run actual `modeld`
- Vision model features (lane detection, object tracking, etc.) will not be functional with this workaround

## Future Improvements
To properly support `modeld` in devcontainers:
1. Ensure NVIDIA driver versions match between host and container
2. Install proper OpenCL ICD loaders and register NVIDIA OpenCL driver
3. Consider using NVIDIA Container Toolkit's OpenCL support
4. Test with different GPU configurations

## Alternative: Running on Host
For full vision model functionality, consider running openpilot directly on the host system instead of in a devcontainer, where GPU/OpenCL access is more straightforward.
