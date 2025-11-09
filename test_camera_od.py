#!/usr/bin/env python3
"""Test if cameraOdometry messages are being published"""
import time
import cereal.messaging as messaging

sm = messaging.SubMaster(['cameraOdometry'])

print("Waiting for cameraOdometry messages...")
for i in range(50):
    sm.update(1000)  # 1 second timeout
    if sm.updated['cameraOdometry']:
        print(f"✓ Received cameraOdometry message! Frame {sm.frame}")
        print(f"  trans: {sm['cameraOdometry'].trans}")
        print(f"  rot: {sm['cameraOdometry'].rot}")
        print(f"  alive: {sm.alive['cameraOdometry']}")
        break
    time.sleep(0.1)
else:
    print("✗ No cameraOdometry messages received after 5 seconds")
    print(f"  alive status: {sm.alive['cameraOdometry']}")
