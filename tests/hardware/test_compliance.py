from .test_camera import TestCamera


class TestCompliance(TestCamera):
    mandatory_PIMA_15740_2000 = set([
        'GetDeviceInfo',
        'OpenSession',
        'CloseSession',
        'GetStorageIDs',
        'GetStorageInfo',
    ])
    mandatory_PIMA_15740_2000_pull = set([
        'GetNumObjects',
        'GetObjectHandles',
        'GetObjectInfo',
        'GetObject',
        'GetThumb',
    ])
    mandatory_PIMA_15740_2000_push = set([
        'SendObjectInfo',
        'SendObject',
    ])
    # Microsoft Windows needs support for PIMA 15740:2000 Pull mode minus
    # 'GetNumObjects'
    windows_required = set(
        op for op in mandatory_PIMA_15740_2000_pull if op != 'GetNumObjects'
    )

    # ISO 15740:2013 is fully backwards compatible with PIMA 15740:2000
    mandatory_ISO_15740_2013 = mandatory_PIMA_15740_2000
    mandatory_ISO_15740_2013_pull = mandatory_PIMA_15740_2000_pull
    mandatory_ISO_15740_2013_push = mandatory_PIMA_15740_2000_push

    def test_PIMA_15740_2000_mandatory(self, device_operations):
        '''
        Verify mandatory commands as specified by PIMA15740:2000
        '''
        supported = set(device_operations)
        assert self.mandatory_PIMA_15740_2000.issubset(supported),\
            'Not all PIMA 15740:2000 mandatory operations are supported.'
        assert self.mandatory_PIMA_15740_2000_pull.issubset(supported) or \
            self.mandatory_PIMA_15740_2000_push.issubset(supported),\
            'PIMA 15740:2000 requires either pull or push mode.'\
            'Neither is supported.'

    def test_ISO_15740_2013_mandatory(self, device_operations):
        '''
        Verify mandatory commands as specified by ISO 15740:2013(E)
        '''
        supported = set(device_operations)
        assert self.mandatory_ISO_15740_2013.issubset(supported)
        assert self.mandatory_ISO_15740_2013_pull.issubset(supported) or \
            self.mandatory_ISO_15740_2013_push.issubset(supported),\
            'ISO 15740:2013(E) requires either pull or push mode.'\
            'Neither is supported.'

    def test_microsoft_windows_support(self, device_operations):
        '''
        Verify commands necessary for Microsoft Windows support.
        '''
        supported = set(device_operations)
        assert self.windows_required.issubset(supported),\
            'Operations for Microsoft Windows support are missing.'
