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


def check_response_code_different(response, value, reason):
    'Check that the value of a response is not value.'
    try:
        assert response.ResponseCode != value, reason
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

        check_response_code_different(
            value,
            'DevicePropNotSupported',
            'Device property is reported to be supported in DeviceInfo, '
            'but then unsupported in GetDevicePropValue'
        )
        check_response_code_different(
            desc,
            'DevicePropNotSupported',
            'Device property is reported to be supported in DeviceInfo, '
            'but then unsupported in ResponseCode for GetDevicePropDesc'
        )
        check_response_code_different(
            set_response,
            'DevicePropNotSupported',
            'Device property is reported to be supported in DeviceInfo, '
            'but then unsupported in SetDevicePropValue'
        )
        check_response_code_different(
            set_response,
            'InvalidDevicePropValue',
            'Setting a property to a value it already has '
            'should never give InvalidDevicePropValue'

        )

        if desc.GetSet == 'Get':
            assert set_response.ResponseCode == 'AccessDenied',\
                'A get-only property should return'\
                ' AccessDenied on SetDevicePropValue.'
        else:
            assert set_response.ResponseCode != 'AccessDenied',\
                'The property is reported as GetSet but access is denied.'


# TODO: test setting all possible values of all possible properties.
