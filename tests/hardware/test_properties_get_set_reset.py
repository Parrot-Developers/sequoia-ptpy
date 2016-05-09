from test_camera import TestCamera


def assert_response_code_different(response, value, reason):
    'Check that the code of a response is not value.'
    try:
        assert response.ResponseCode != value, reason
    except AttributeError:
        pass


class TestGetSetResetProperties(TestCamera):
    def test_get_set_property(self, camera, device_property):
        '''Set property to their current value to check for writability'''
        with camera.session():
            value = camera.get_device_prop_value(device_property)
            desc = camera.get_device_prop_desc(device_property)
            set_response = camera.set_device_prop_value(
                device_property,
                value.Data
            )

            assert_response_code_different(
                value,
                'DevicePropNotSupported',
                'Device property is reported to be supported in DeviceInfo, '
                'but then unsupported in GetDevicePropValue'
            )
            assert_response_code_different(
                desc,
                'DevicePropNotSupported',
                'Device property is reported to be supported in DeviceInfo, '
                'but then unsupported in ResponseCode for GetDevicePropDesc'
            )
            assert_response_code_different(
                set_response,
                'DevicePropNotSupported',
                'Device property is reported to be supported in DeviceInfo, '
                'but then unsupported in SetDevicePropValue'
            )
            assert_response_code_different(
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

    def test_reset_property(self, camera, device_property):
        '''Set property to their current value to check for writability'''
        with camera.session():
            reset = camera.reset_device_prop_value(device_property)
            assert_response_code_different(
                reset,
                'DevicePropNotSupported',
                'Device property is reported to be supported in DeviceInfo, '
                'but then unsupported in ResetDevicePropValue'
            )
            desc = camera.get_device_prop_desc(device_property)
            assert desc.CurrentValue == desc.FactoryDefaultValue,\
                'The value after ResetDevicePropValue '\
                'and the FactoryDefaultValue differ.'

    # TODO: test setting all possible values of all possible properties.
