from ...test_camera import TestCamera
import pytest


@pytest.mark.incremental
class TestSequoia(TestCamera):
    @pytest.fixture(autouse=True)
    def sequoia(self, camera):
        device_info = camera.get_device_info()
        if 'Sequoia' not in device_info.Model:
            pytest.skip('The camera is not a Sequoia')
        return camera
