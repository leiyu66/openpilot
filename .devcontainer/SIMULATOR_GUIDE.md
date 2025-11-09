# openpilot Simulator Guide

## Prerequisites

The dev container has been configured with all necessary dependencies:
- Python 3.11
- Build tools (clang, cmake, scons)
- System libraries (OpenCL, ZMQ, Eigen3, FFmpeg, etc.)
- Git LFS for large binary files

## Starting the Simulator

### Step 1: Launch openpilot (Terminal 1)

```bash
cd /workspaces/openpilot
./tools/sim/launch_openpilot.sh
```

This will start the openpilot manager process and UI. You should see:
- Manager initialization messages
- UI window opening (if display is available)
- Various daemon processes starting

### Step 2: Launch the Bridge (Terminal 2)

In a new terminal:

```bash
cd /workspaces/openpilot/tools/sim
./run_bridge.py
```

The bridge connects openpilot to the simulator and allows you to control the vehicle.

## Controls

Once both processes are running:

- **Press 1**: Decrease cruise speed
- **Press 2**: Engage/disengage cruise control
- **Press 3**: Increase cruise speed
- **W/A/S/D**: Manual steering and acceleration (when not engaged)
- **Q**: Quit simulator

## Configuration

### Font Size

If fonts appear too large or too small in the UI, adjust the `FONT_SCALE` environment variable:

```bash
# Smaller fonts (default in dev container is 0.8)
export FONT_SCALE=0.8

# Default openpilot font size
export FONT_SCALE=1.242

# Even smaller
export FONT_SCALE=0.6
```

Then restart openpilot:
```bash
./tools/sim/launch_openpilot.sh
```

You can also set this permanently in `.devcontainer/devcontainer.json` under `containerEnv`.

## Troubleshooting

### Missing bootlog warning
If you see `FileNotFoundError: './bootlog'`, this is non-critical and can be ignored.

### Font loading errors
Font errors like "Failed to open text file" are non-critical - the UI will use default fonts.

### Build errors
If modules are missing, rebuild with:
```bash
scons -j$(nproc) --minimal
```

### Git LFS files not downloaded
If you see text files instead of binaries:
```bash
git lfs install
git submodule update --init --recursive
cd third_party/acados && git lfs pull
```

## Architecture

The simulator consists of:
1. **openpilot** - The main autonomous driving stack
2. **Bridge** - Connects openpilot to the driving simulator
3. **Manager** - Orchestrates all openpilot processes
4. **UI** - Visual interface for monitoring

## Key Components Built

The postCreateCommand automatically builds:
- `msgq` - Inter-process communication
- `modeld` - Machine learning models for perception
- `rednose` - Kalman filtering for localization
- `pandad` - CAN bus interface
- `longitudinal_mpc_lib` - Model predictive control for acceleration/braking
- `common/transformations` - Coordinate transformations

## Additional Resources

- [openpilot Documentation](https://docs.comma.ai)
- [Simulator README](../../tools/sim/README.md)
- [Contributing Guide](../../docs/CONTRIBUTING.md)
