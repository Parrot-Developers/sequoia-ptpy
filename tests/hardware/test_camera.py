import pytest


@pytest.mark.incremental
@pytest.mark.usefixtures('cam')
class TestCamera:
    '''Perform tests on a physical camera.'''
    def test_device_info(self, cam):
        '''Camera responds to PTP.'''
        if cam is None:
            pytest.skip('No camera available to test')

        device_info = cam.get_device_info()
        assert device_info, 'There is no response for DeviceInfo.\n'\
            'The camera may not support PTP.'
        # TODO: Check for mandatory  operations and properties according to PTP
        # version 1.0 or 1.1
