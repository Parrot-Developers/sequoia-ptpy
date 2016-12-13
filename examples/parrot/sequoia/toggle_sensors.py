#!/usr/bin/env python
from ptpy import PTPy
from time import sleep

camera = PTPy()

with camera.session():
    tries = 0
    keep_on = camera.get_device_prop_desc('PhotoSensorsKeepOn')
    state = keep_on.CurrentValue
    while keep_on.CurrentValue == state and tries < 10:
        tries += 1
        sleep(1)
        attempt = camera.set_device_prop_value('PhotoSensorsKeepOn', int(not state))
        keep_on = camera.get_device_prop_desc('PhotoSensorsKeepOn')
        print('Tries:{}'.format(tries))
        print('Attempt response: {}'.format(attempt))
        print('Current value: {}'.format(keep_on))
