#!/usr/bin/env python
import ptpy

camera = ptpy.PTPy()

with camera.session():
    device_info = camera.get_device_info()
    for prop in device_info.DevicePropertiesSupported:
        print(camera.get_device_prop_desc(prop))
