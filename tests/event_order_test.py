#!/usr/bin/env python
from ptpy.usb_transport import USBTransport
# TODO Fix import once ptpy module is better structured.
from time import time


def test_order():
    camera = USBTransport()
    with camera.session():
        tic = time()
        # Clear all events for ten seconds.
        print('Clearing all events')
        while time() - tic < 10:
            evt = camera.event()
        print('Initiating capture')
        capture = camera.initiate_capture()
        codes = []
        tic = time()
        print('Waiting for capture events 10s')
        while time() - tic < 10:
            evt = camera.event()
            if evt:
                print evt
                if evt.TransactionID == capture.TransactionID:
                    codes.append(evt.EventCode)

        assert('CaptureComplete' in codes)
        assert('ObjectAdded' in codes)
        assert(codes.index('ObjectAdded') < codes.index('CaptureComplete'))
