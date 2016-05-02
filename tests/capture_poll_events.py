#!/usr/bin/env python
from ptpy.usb_transport import USBTransport
# TODO Fix import once ptpy module is better structured.

camera = USBTransport()
with camera.session():
    print('Initiating capture')
    print(camera.initiate_capture())
    while True:
        evt = camera.event()
        if evt:
            print(evt)
