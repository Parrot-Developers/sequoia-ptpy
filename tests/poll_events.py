#!/usr/bin/env python
from ptpy.usb_transport import USBTransport
# TODO Fix import once ptpy module is better structured.

camera = USBTransport()
with camera.session():
    while True:
        evt = camera.event()
        if evt:
            print evt
