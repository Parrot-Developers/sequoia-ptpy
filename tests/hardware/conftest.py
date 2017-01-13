from ..context import ptpy
import pytest

available_camera = None
try:
    available_camera = ptpy.PTPy(knowledge=False)
except Exception as e:
    print(e)
    pass


# Use the same camera for a testing session. And skip all tests that use it.
@pytest.fixture(scope='session', autouse=True)
def camera():
    if available_camera is None:
        if not pytest.config.getoption('--expect-camera'):
            pytest.skip('No camera available to test')
        else:
            pytest.fail('Expected a camera but None was found')
    return available_camera


# Each test gets the latest operations and properties supported, since these
# may change on different functional modes.
@pytest.fixture(scope='function', autouse=True)
def device_properties(camera):
    device_props = (
        camera.get_device_info().DevicePropertiesSupported if camera else []
    )
    return device_props


@pytest.fixture(scope='function', autouse=True)
def device_operations(camera):
    device_ops = (
        camera.get_device_info().OperationsSupported if camera else []
    )
    return device_ops


# TODO: This is a hacky solution to the lack of fixtures in parametrize. It
# should be expunged if pytests ends up fixing that.
def pytest_generate_tests(metafunc):
    if 'device_property' in metafunc.fixturenames:
        device_properties = (
            available_camera.get_device_info().DevicePropertiesSupported if
            available_camera else []
        )
        metafunc.parametrize('device_property', device_properties)
    if 'device_operation' in metafunc.fixturenames:
        device_operations = (
            available_camera.get_device_info().OperationsSupported if
            available_camera else []
        )
        metafunc.parametrize('device_property', device_operations)
