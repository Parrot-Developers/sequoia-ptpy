#!/usr/bin/env python
from ptpy.usb_transport import USBTransport
# TODO Fix import once ptpy module is better structured.
from time import time

camera = USBTransport()
with camera.session():
    tic = time()
    # Clear all events for ten seconds.
    while time() - tic < 10:
        evt = camera.event()
    print('Initiating capture')
    capture = camera.initiate_capture()
    evts = []
    tic = time()
    print('Waiting for events 10s.')
    while time() - tic < 10:
        evt = camera.event()
        if evt:
            print evt
            if evt.TransactionID == capture.TransactionID:
                evts.append(evt)

    codes = [x.EventCode for x in evts]
    print codes

    if 'CaptureComplete' not in codes:
        raise Exception('No CaptureComplete received.')

    if 'ObjectAdded' not in codes:
        raise Exception('No ObjectAdded received.')

    if codes.index('ObjectAdded') > codes.index('CaptureComplete'):
        raise Exception(
            'Incorrect order: '
            'ObjectAdded after CaptureCompleted for same transaction.'
        )

    print('Success!')
