#!/usr/bin/env python3
"""Test if modelV2 messages are being published"""
import time
import cereal.messaging as messaging

sm = messaging.SubMaster(['modelV2'])

print("Waiting for modelV2 messages...")
for _ in range(50):
    sm.update(1000)  # 1 second timeout
    if sm.updated['modelV2']:
        print(f"✓ Received modelV2 message! Frame {sm.frame}")
        print(f"  frameId: {sm['modelV2'].frameId}")
        print(f"  alive: {sm.alive['modelV2']}")
        break
    time.sleep(0.1)
else:
    print("✗ No modelV2 messages received after 5 seconds")
    print(f"  alive status: {sm.alive['modelV2']}")
