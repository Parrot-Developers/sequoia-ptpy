# TODO Fix import once ptpy module is better structured.
from ptpy.usb_transport import USBTransport
import pytest

# TODO: Refactor getting camera for all hardware tests.
camera = None
try:
    camera = USBTransport()
except Exception:
    pass

device_info = camera.get_device_info() if camera else []


def check_response_code_different(response, value):
    'Check that the value of a response is not value.'
    try:
        response.ResponseCode != value
    except AttributeError:
        pass


@pytest.mark.skipif(camera is None, reason='No camera available to test')
@pytest.mark.parametrize('prop', device_info.DevicePropertiesSupported)
def test_get_set_property(prop):
    '''Set property to their current value to check for writability'''
    with camera.session():
        value = camera.get_device_prop_value(prop)
        desc = camera.get_device_prop_desc(prop)
        set_response = camera.set_device_prop_value(prop, value.Data)

        check_response_code_different(value, 'DevicePropNotSupported')
        check_response_code_different(desc, 'DevicePropNotSupported')
        check_response_code_different(set_response, 'DevicePropNotSupported')
        check_response_code_different(set_response, 'InvalidDevicePropValue')

        if desc.GetSet == 'Get':
            assert set_response.ResponseCode == 'AccessDenied',\
                'A get-only property should return'\
                ' AccessDenied on SetDevicePropValue.'
        else:
            assert set_response.ResponseCode != 'AccessDenied',\
                'The property is reported as GetSet but access is denied.'


# TODO: test setting all possible values of all possible properties.
