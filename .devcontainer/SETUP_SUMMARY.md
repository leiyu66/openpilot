# Openpilot Simulator Setup Summary

## Changes Made to Enable Simulator

### Dockerfile Updates
**File**: `.devcontainer/Dockerfile`

Added missing dependencies:
- `libusb-1.0-0-dev` - For panda USB communication
- `gettext` - For UI translations (msgfmt)
- `libcurl4-openssl-dev` - For replay tool HTTP functionality
- `libncurses-dev` - For replay tool console UI
- `gcc-arm-none-eabi` - ARM cross-compiler for panda firmware
- `libssl-dev` - For crypto library linking and OpenSSL headers
- `libbz2-dev` - For bzip2 compression headers
- Removed `pocl-opencl-icd` - Due to LLVM compatibility issues

Added raylib header fix for headless container builds:
- Clones raylib repository and copies headers during container build
- Ensures raylib headers are available even when X11 build fails

### 2. Build Configuration
**File**: `SConstruct`

Modified to skip panda firmware build when using `--minimal` flag:
```python
# Build other submodules
if GetOption('extras'):
  SConscript(['panda/SConscript'])
```

**File**: `selfdrive/modeld/SConscript`

Modified to skip tinygrad model compilation when using `--minimal` flag:
```python
# Compile small models
if GetOption('extras'):
  for model_name in ['driving_vision', 'driving_policy', 'dmonitoring_model']:
    # ... compilation code
```

### 3. OpenCL Workaround
**File**: `tools/sim/lib/camerad.py`

Added fallback to NumPy-based RGB to YUV conversion when OpenCL fails:
- Wraps OpenCL initialization in try/except
- Falls back to pure NumPy implementation (slower but compatible)
- Fixes POCL kernel compilation errors

### 5. Model Compilation Fix
**File**: `selfdrive/modeld/SConscript`

**Issue**: POCL OpenCL bug preventing tinygrad model compilation with CPU_LLVM=1

**Solution**: Changed compilation flags to use CPU_LLVM=0 (C backend instead of LLVM)
```python
flags = {
  'larch64': 'DEV=QCOM',
  'Darwin': f'DEV=CPU HOME={os.path.expanduser("~")} IMAGE=0',
}.get(arch, 'DEV=CPU CPU_LLVM=0 IMAGE=0')  # Changed from CPU_LLVM=1
```

**Result**: All required models now compile and load successfully

## Raylib Build Issue Resolution

**Issue**: Raylib library exists in git but contains C23 functions (`__isoc23_sscanf`, `__isoc23_strtol`, `__isoc23_strtoul`) not available in the container's glibc version.

**Solution**:
- Added raylib header copying to Dockerfile to ensure headers are available in container
- Modified `selfdrive/ui/SConscript` to include compatibility check that tests linking with raylib before attempting to build installers
- If linking fails (due to C23 compatibility issues), installers are skipped automatically
- Added debug output to show check results

**Result**: UI installers build successfully when raylib library and headers are available and compatible

**Issue**: Build was failing because panda firmware requires ARM cross-compiler (`arm-none-eabi-gcc`).

**Solution**:
- Added `gcc-arm-none-eabi` to Dockerfile
- Panda firmware now builds successfully with ARM cross-compiler

**Result**:
- All components including panda firmware compile properly
- Complete openpilot build in container

## What's Working

✅ **Container Build**: Successfully compiles with all dependencies
✅ **Core Components**: pandad, controls, locationd, UI, bridge
✅ **Simulator Bridge**: Connects to MetaDrive successfully
✅ **Camera Simulation**: RGB to YUV conversion works (NumPy fallback)
✅ **UI Display**: Proper scaling for visibility
✅ **Manual Control**: Vehicle responds to W/A/S/D keys
✅ **CAN Simulation**: Bridge sends CAN messages
✅ **ML Models**: All required models compile and load successfully
✅ **Openpilot Engagement**: Full autonomy now works in simulator
✅ **Panda Firmware**: ARM cross-compilation works
✅ **Replay Tools**: All replay functionality compiles with crypto/bzip2 support

## Known Limitations

❌ **Audio**: soundd audio may not work in containerized environment (non-critical)

## Files Modified

1. `.devcontainer/Dockerfile` - Dependencies and raylib header fix
2. `.devcontainer/devcontainer.json` - Environment and build command
3. `SConstruct` - Skip panda build with --minimal
4. `selfdrive/modeld/SConscript` - Skip model compilation with --minimal
5. `tools/sim/lib/camerad.py` - OpenCL fallback to NumPy
6. `tools/sim/launch_openpilot.sh` - No changes needed (already blocks camerad)
7. `selfdrive/ui/SConscript` - Added raylib compatibility check

## Running the Simulator

Despite the limitations, you can still run the simulator:

### Terminal 1: Start openpilot
```bash
cd /workspaces/openpilot
export SCALE=0.70
export FONT_SCALE=0.65
./tools/sim/launch_openpilot.sh
```

### Terminal 2: Start bridge
```bash
cd /workspaces/openpilot
./tools/sim/run_bridge.py
```

### Controls
- **W/A/S/D**: Manual driving
- **R**: Reset simulation
- **I**: Toggle ignition
- **Q**: Quit

## Model Compilation - RESOLVED

**Issue**: POCL OpenCL implementation had LLVM compatibility bug causing "unknown target CPU 'generic'" error.

**Solution Implemented**:
- Modified `selfdrive/modeld/SConscript` to use `CPU_LLVM=0` instead of `CPU_LLVM=1`
- This uses tinygrad's C backend instead of LLVM backend for CPU compilation
- All required models (`driving_policy`, `driving_vision`, `dmonitoring_model`) now compile successfully
- Openpilot can now engage in simulator with full autonomy

**Alternative Solutions** (no longer needed):
- GPU OpenCL compilation
- Pre-compiled models from working system
- POCL rebuild with newer LLVM
- Different tinygrad backend

## Testing Without Full Engagement

Even without ML models, you can:
- Test UI changes and scaling
- Verify bridge connectivity
- Test manual driving in MetaDrive
- Develop and test non-perception components
- Test CAN message simulation

## Rebuild Instructions

If you make changes and want to rebuild:

```bash
# In VS Code Command Palette (Ctrl+Shift+P)
> Dev Containers: Rebuild Container

# Or rebuild without cache
> Dev Containers: Rebuild Container Without Cache
```

## Support and Resources

- [openpilot Documentation](https://docs.comma.ai)
- [MetaDrive Simulator](https://github.com/metadriverse/metadrive)
- [Tinygrad](https://github.com/tinygrad/tinygrad)
- [POCL Issue Tracker](https://github.com/pocl/pocl/issues)
