from ptpy.usb_transport import USBTransport
# TODO Fix import once ptpy module is better structured.
from time import time
import pytest

camera = None
try:
    camera = USBTransport()
except Exception:
    pass


@pytest.mark.skipif(camera is None, reason='No camera available to test')
def test_order():
    with camera.session():
        tic = time()
        print('Clearing all events (10s)')
        while time() - tic < 10:
            evt = camera.event()
        print('Initiating capture')
        capture = camera.initiate_capture()
        codes = []
        tic = time()
        print('Waiting for capture events (10s)')
        while time() - tic < 10:
            evt = camera.event()
            if evt:
                print evt
                if evt.TransactionID == capture.TransactionID:
                    codes.append(evt.EventCode)

        assert('CaptureComplete' in codes)
        assert('ObjectAdded' in codes)
        capture_complete_index = codes.index('CaptureComplete')
        last_object_added_index = (
            (len(codes) - 1) - codes[::-1].index('ObjectAdded')
        )
        assert(last_object_added_index < capture_complete_index)
