# TODO Fix import once ptpy module is better structured.
from time import time
from test_camera import TestCamera
import pytest


class TestCapture(TestCamera):
    def test_order(self, camera):
        device_info = camera.get_device_info()
        print device_info
        if 'InitiateCapture' not in device_info.OperationsSupported:
            pytest.skip('InitiateCapture is not supported by camera.')

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

            assert 'CaptureComplete' in codes, 'No CaptureComplete received.'
            assert 'ObjectAdded' in codes,\
                'No ObjectAdded received for capture transaction.'
            capture_complete_index = codes.index('CaptureComplete')
            last_object_added_index = (
                (len(codes) - 1) - codes[::-1].index('ObjectAdded')
            )
            assert last_object_added_index < capture_complete_index,\
                'ObjectAdded happened after CaptureComplete.'
