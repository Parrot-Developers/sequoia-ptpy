from ..context import ptpy
from ptpy.usb_transport import USBTransport
# TODO Fix import once ptpy module is better structured.
import pytest

available_camera = None
try:
    available_camera = USBTransport()
except Exception:
    pass


# Use the same camera for a testing session.
@pytest.fixture(scope='session', autouse=True)
def camera():
    return available_camera


# Each test gets the latest operations and properties supported, since these
# may change on different functional modes.
@pytest.fixture(scope='function', autouse=True)
def device_properties(camera):
    device_info = camera.get_device_info()
    return device_info.DevicePropertiesSupported


@pytest.fixture(scope='function', autouse=True)
def device_operations(camera):
    device_info = camera.get_device_info()
    return device_info.OperationsSupported


# TODO: This is a hacky solution to the lack of fixtures in parametrize. It
# should be expunged if pytests ends up fixing that.
def pytest_generate_tests(metafunc):
    if 'device_property' in metafunc.fixturenames:
        device_properties = (
            available_camera.get_device_info().DevicePropertiesSupported
        )
        metafunc.parametrize('device_property', device_properties)
    if 'device_operation' in metafunc.fixturenames:
        device_operations = (
            available_camera.get_device_info().OperationsSupported
        )
        metafunc.parametrize('device_property', device_operations)
