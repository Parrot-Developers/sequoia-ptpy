from time import time
from .test_camera import TestCamera
import pytest


class TestCapture(TestCamera):
    def test_event_order(self, camera):
        device_info = camera.get_device_info()
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
                    print(evt)
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


class TestOpenCapture(TestCamera):
    def test_termination(self, camera):
        '''Verify TerminateOpenCapture behaviour.'''
        device_info = camera.get_device_info()
        if 'InitiateOpenCapture' not in device_info.OperationsSupported:
            pytest.skip('InitiateOpenCapture is not supported by camera.')

        with camera.session():
            capture = camera.initiate_open_capture()
            # Attempt to close the wrong open capture.
            wrong_transaction = camera.terminate_open_capture(
                capture.TransactionID + 1
            )
            right_transaction = camera.terminate_open_capture(
                capture.TransactionID
            )

            assert wrong_transaction.ResponseCode ==\
                'InvalidTransactionID',\
                \
                'When terminating the wrong open capture, '\
                'we expect InvalidTransactionID as ResponseCode.'

            assert right_transaction.ResponseCode != 'InvalidTransactionID',\
                'The response should never be InvalidTransactionID '\
                'for the right transaction.'

            assert (
                right_transaction.ResponseCode == 'OK' or
                right_transaction.ResponseCode == 'CaptureAlreadyTerminated'
            ),\
                'When terminating the correct open capture, '\
                'we expect the session to be successfully closed '\
                'or already closed.'
