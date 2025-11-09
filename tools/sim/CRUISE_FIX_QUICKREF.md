# Quick Reference: Cruise Button Fix

## What was the problem?
Pressing '2' immediately after starting the bridge caused:
- ❌ "Communication Issue Between Processes"
- ❌ "Posenet Speed Invalid"

## Why did it happen?
The vision model (`modeld`) needs time to start publishing `cameraOdometry` messages.
Pressing '2' before these messages start causes `locationd` to fail its health checks.

## What's the fix?
The bridge now waits for all critical processes to initialize before allowing cruise engagement.

## How to use:
1. Start the bridge: `./tools/sim/run_bridge.py`
2. Press '2' - you'll see: **"⚠ System initializing... Please wait"**
3. Wait ~1 second until: **"✓ System ready - all processes initialized"**
4. Press '2' again - cruise control engages normally! ✓

## Status Indicators:
```
⚠ System initializing... Please wait
  livePose: ✓
  cameraOdometry: ✗  ← Still starting up
  modelV2: ✓
  posenetOK: ✗

... wait a moment ...

✓ System ready - all processes initialized
  You can now press '2' to engage cruise control
```

## For Developers:

### Key Variables:
- `WARMUP_FRAMES = 100` (~1 second)
- `self.warmup_complete` - tracks if initialization is done
- `sm_monitor` - monitors critical message streams

### Bypassing for Tests:
The check is automatically bypassed when `test_run=True`

### Modified Files:
1. `tools/sim/bridge/common.py` - Main warmup logic
2. `selfdrive/locationd/locationd.py` - More lenient spike detection

## Troubleshooting:

### Still seeing errors?
Check if all processes are running:
```bash
ps aux | grep -E "modeld|locationd|selfdrived"
```

### Taking too long to initialize?
Check message flow:
```python
# In another terminal
from cereal import messaging
sm = messaging.SubMaster(['cameraOdometry', 'livePose'])
while True:
    sm.update(100)
    print(f"cameraOdometry: {sm.alive['cameraOdometry']}, livePose: {sm.alive['livePose']}")
```

### Want to skip the check?
Only for development/testing:
```python
# In bridge initialization
self.warmup_complete = True  # Skip warmup check
```
