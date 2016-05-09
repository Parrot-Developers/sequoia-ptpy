#!/usr/bin/env python
from ptpy.usb_transport import USBTransport
# TODO Fix import once ptpy module is better structured.

camera = USBTransport()
with camera.session():
    print('Initiating open capture')
    capture = camera.initiate_open_capture()
    print(capture)
    try:
        while True:
            evt = camera.event()
            if evt:
                print(evt)
    except KeyboardInterrupt:
        pass
    finally:
        if capture.ResponseCode == 'OK':
            print('Terminating open capture.')
            print(camera.terminate_open_capture(capture.TransactionID))
