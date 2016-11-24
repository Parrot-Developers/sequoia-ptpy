from .test_camera import TestCamera
from construct import Computed, Struct


def assert_response_code_different(response, value, reason):
    'Check that the code of a response is not value.'
    try:
        assert response.ResponseCode != value, reason
    except AttributeError:
        pass


def assert_response_code_equal(response, value, reason):
    'Check that the code of a response is not value.'
    try:
        assert response.ResponseCode == value, reason
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
                assert_response_code_equal(
                    set_response,
                    'AccessDenied',
                    'A get-only property should return '
                    'AccessDenied on SetDevicePropValue.'
                )
            else:
                assert_response_code_different(
                    set_response,
                    'AccessDenied',
                    'The property is reported as GetSet but access is denied.'
                )

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

    def test_desc_get_property_identical(self, camera, device_property):
        '''
        Check property description and property get share the same value.

        GetDevicePropValue == GetDevicePropDesc.CurrentValue
        '''
        with camera.session():
            value = camera.get_device_prop_value(device_property)
            desc = camera.get_device_prop_desc(device_property)
            # TODO: refactor this into PTPy core to automatically parse and
            # build properties for which a GetDevicePropDesc has been issued.
            builder = 'Builder' / Struct(
                'DataTypeCode' / Computed(lambda ctx: desc.DataTypeCode),
                'CurrentValue' / camera._DataType
                )
            data = builder.build(desc)
            assert value.Data == data,\
                'GetDevicePropDesc.CurrentValue and '\
                'GetDevicePropValue should match.'

    # TODO: test setting all possible values of all possible properties.
