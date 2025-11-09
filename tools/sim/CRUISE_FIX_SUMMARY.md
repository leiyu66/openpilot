# Fix for "Communication errors between Processes" and "Posenet speed invalid" when pressing '2' in bridge

## Problem Description

When pressing the '2' key immediately after starting the simulator bridge, users would encounter:
1. **Communication Issue Between Processes** error
2. **Posenet Speed Invalid** error

This prevented cruise control from engaging properly.

## Root Cause

The issue occurred due to a race condition during system initialization:

1. The simulator bridge starts multiple processes (modeld, locationd, etc.)
2. The `cameraOdometry` message is published by `modeld` (vision model), not the simulator sensors
3. `locationd` needs `cameraOdometry` messages to update `posenet_stds` properly
4. When pressing '2' too early, `cameraOdometry` messages haven't started flowing yet
5. This causes `posenetOK` to be false, triggering both errors

## Solution

### 1. Added Warmup Period in Bridge (`tools/sim/bridge/common.py`)

- **WARMUP_FRAMES = 100** (~1 second at 100Hz) to allow all processes to initialize
- Monitor critical messages: `livePose`, `cameraOdometry`, `modelV2`
- Check `posenetOK` status from `livePose`
- Block cruise button commands until warmup is complete
- Provide user feedback showing initialization status

**Key Changes:**
```python
# Added warmup tracking
self.warmup_complete = False
self.last_cruise_button_warning = 0

# Monitor system readiness
sm_monitor = messaging.SubMaster(['livePose', 'cameraOdometry', 'modelV2'])

# Check warmup status
if self.rk.frame > WARMUP_FRAMES and not self.warmup_complete:
    if all critical messages are alive and posenetOK:
        self.warmup_complete = True
        print("✓ System ready - all processes initialized")

# Block cruise commands during warmup
if not self.warmup_complete and not self.test_run:
    print("⚠ System initializing... Please wait")
    # Show status of each component
    continue  # Skip processing the cruise command
```

### 2. More Lenient Spike Detection (`selfdrive/locationd/locationd.py`)

Made the `posenetOK` check more forgiving during initialization:
- Detection threshold: 8.0 during init (vs 4.0 normally)
- Prevents false positives when posenet_stds is still at initial values

```python
is_initializing = old_mean >= POSENET_STD_INITIAL_VALUE * 0.9
std_spike_threshold = 8.0 if is_initializing else 4.0
std_spike = (new_mean / old_mean) > std_spike_threshold and new_mean > 7.0
```

## User Experience

### Before Fix:
1. Start bridge: `./tools/sim/run_bridge.py`
2. Press '2' immediately
3. ❌ Get "Communication errors" and "Posenet speed invalid"
4. System doesn't engage

### After Fix:
1. Start bridge: `./tools/sim/run_bridge.py`
2. Press '2' immediately
3. ✅ See: "⚠ System initializing... Please wait" with status indicators
4. Wait ~1 second
5. ✅ See: "✓ System ready - all processes initialized"
6. Press '2' again
7. ✅ Cruise control engages normally

## Testing

Run the test script to verify:
```bash
cd /workspaces/openpilot
python3 tools/sim/test_cruise_fix.py
```

Or test manually:
```bash
./tools/sim/run_bridge.py
# Press '2' immediately - should see initialization message
# Wait for "System ready" message
# Press '2' again - should engage successfully
```

## Files Modified

1. **`tools/sim/bridge/common.py`**
   - Added warmup period tracking
   - Added system readiness monitoring
   - Block cruise commands until ready
   - User feedback for initialization status

2. **`selfdrive/locationd/locationd.py`**
   - More lenient spike detection during initialization
   - Prevents false posenetOK failures at startup

## Technical Details

### Message Flow:
```
Camera Images → modeld → cameraOdometry → locationd → livePose
                                              ↓
                                         posenet_stds
                                              ↓
                                         posenetOK flag
                                              ↓
                                        selfdrived checks
```

### Initialization Sequence:
1. Bridge starts (frame 0)
2. World ticks 20 times (warmup)
3. Processes start publishing messages
4. Monitor waits for WARMUP_FRAMES (100 frames)
5. Check all messages are alive and valid
6. Set `warmup_complete = True`
7. Allow cruise button commands

## Benefits

- ✅ Eliminates race condition errors at startup
- ✅ Clear user feedback during initialization
- ✅ No impact on normal operation after warmup
- ✅ Test mode bypasses check for automated testing
- ✅ More robust initialization sequence
