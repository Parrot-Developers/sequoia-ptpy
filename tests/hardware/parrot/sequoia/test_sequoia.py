from ...test_camera import TestCamera
import pytest


class TestSequoia(TestCamera):
    def test_model(self, camera):
        device_info = camera.get_device_info()
        if 'Sequoia' not in device_info.Model:
            pytest.skip('The camera is not a Sequoia')

    @pytest.fixture()
    def sequoia(self, camera):
        return camera
