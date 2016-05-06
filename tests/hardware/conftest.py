from ptpy.usb_transport import USBTransport
# TODO Fix import once ptpy module is better structured.
import pytest

available_camera = None
try:
    available_camera = USBTransport()
except Exception:
    pass


@pytest.fixture(scope='session', autouse=True)
def cam():
    return available_camera
