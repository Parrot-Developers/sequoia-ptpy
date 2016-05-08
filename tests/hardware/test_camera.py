import pytest


@pytest.mark.incremental
@pytest.mark.usefixtures('camera')
class TestCamera:
    '''Perform tests on a physical camera.'''
    def test_device_info(self, camera):
        '''Camera responds to PTP.'''
        if camera is None:
            pytest.skip('No camera available to test')

        device_info = camera.get_device_info()
        assert device_info, 'There is no response for DeviceInfo.\n'\
            'The camera may not support PTP.'
