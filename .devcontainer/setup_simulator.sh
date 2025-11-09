#!/bin/bash
set -e

echo "Setting up openpilot for simulator..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --no-cache-dir -e .[dev,tools]

# Build only what's needed for simulator (skip panda and models)
echo "Building core components..."
scons -j$(nproc) --minimal

echo "Setup complete! You can now run the simulator with:"
echo "  Terminal 1: ./tools/sim/launch_openpilot.sh"
echo "  Terminal 2: ./tools/sim/run_bridge.py"
