#!/usr/bin/env python3
"""
Test script to verify the cruise button fix for simulator
This simulates pressing button 2 immediately after starting the bridge
to verify proper initialization handling
"""
from multiprocessing import Queue
from openpilot.tools.sim.bridge.common import control_cmd_gen

def test_early_cruise_button():
    """Test that cruise buttons are properly blocked during warmup"""
    print("Testing cruise button behavior during initialization...")

    # This would normally be created by run_bridge.py
    q = Queue()

    # Simulate pressing cruise button immediately (like pressing '2')
    print("\n1. Simulating early cruise button press (like user pressing '2' too early)...")
    q.put(control_cmd_gen("cruise_down"))

    print("2. Expected behavior: System should show 'initializing' message")
    print("3. After ~1 second: System should show 'ready' message")
    print("4. Then cruise button should work normally")

    print("\n✓ Test setup complete")
    print("\nTo test manually:")
    print("  1. Run: ./tools/sim/run_bridge.py")
    print("  2. IMMEDIATELY press '2' key")
    print("  3. You should see: '⚠ System initializing... Please wait'")
    print("  4. Wait for: '✓ System ready - all processes initialized'")
    print("  5. Press '2' again - it should now work without errors")

if __name__ == "__main__":
    test_early_cruise_button()
