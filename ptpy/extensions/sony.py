'''This module extends PTPDevice for Sony devices.

Use it in a master module that determines the vendor and automatically uses its
extension. This is why inheritance is not explicit.
'''
from contextlib import contextmanager
from construct import Container, Struct, Range
import logging
logger = logging.getLogger(__name__)

__all__ = ('Sony',)


class Sony(object):
    '''This class implements Sony's PTP operations.'''
    def __init__(self, *args, **kwargs):
        logger.debug('Init Sony')
        super(Sony, self).__init__(*args, **kwargs)
        # TODO: expose the choice to poll or not Sony events

    @contextmanager
    def session(self):
        '''
        Manage Sony session with context manager.
        '''
        # When raw device, do not perform
        logger.debug('Session Sony')
        with super(Sony, self).session():
            yield

    def _shutdown(self):
        logger.debug('Shutdown Sony')
        super(Sony, self)._shutdown()

    def _PropertyCode(self, **product_properties):
        return super(Sony, self)._PropertyCode(
            DPCCompensation=0xD200,
            DRangeOptimize=0xD201,
            SonyImageSize=0xD203,
            ShutterSpeed=0xD20D,
            ColorTemp=0xD20F,
            CCFilter=0xD210,
            AspectRatio=0xD211,
            FocusFound=0xD213,
            ObjectInMemory=0xD215,
            ExposeIndex=0xD216,
            SonyBatteryLevel=0xD218,
            PictureEffect=0xD21B,
            ABFilter=0xD21C,
            ISO=0xD21E,
            AutoFocus=0xD2C1,
            Capture=0xD2C2,
            Movie=0xD2C8,
            StillImage=0xD2C7,
            **product_properties
        )

    def _OperationCode(self, **product_operations):
        return super(Sony, self)._OperationCode(
            SDIOConnect=0x9201,
            SDIOGetExtDeviceInfo=0x9202,
            SonyGetDevicePropDesc=0x9203,
            SonyGetDevicePropValue=0x9204,
            SetControlDeviceA=0x9205,
            GetControlDeviceDesc=0x9206,
            SetControlDeviceB=0x9207,
            GetAllDevicePropData=0x9209,
            **product_operations
        )

    def _ObjectFormatCode(self, **product_object_formats):
        return super(Sony, self)._ObjectFormatCode(
            SonyFormat1=0xb301,
            RAW=0xb101,

            **product_object_formats
        )

    def _ResponseCode(self, **product_responses):
        return super(Sony, self)._ResponseCode(
            Sony1=0xa101,
            **product_responses
        )

    def _EventCode(self, **product_events):
        return super(Sony, self)._EventCode(
            SonyObjectAdded=0xc201,
            SonyObjectRemoved=0xc202,
            SonyPropertyChanged=0xc203,
            **product_events
        )

    def _FilesystemType(self, **product_filesystem_types):
        return super(Sony, self)._FilesystemType(
            **product_filesystem_types
        )

    def _SonyDeviceInfo(self):
        # TODO: Verify how many arrays we can get.
        return Range(0, 3, self._PTPArray(self._UInt16))

    def _SonyPropDesc(self):
        return Struct(
            'PropertyCode' / self._PropertyCode,
            'DataTypeCode' / self._DataTypeCode,
            'GetSet' / self._GetSet,
            'Sony1' / self._UInt8,
            'Value' / self._DataType,
            'FactoryDefaultValue' / self._DataType,
            'CurrentValue' / self._DataType,
        )

    def _set_endian(self, endian):
        logger.debug('Set Sony endianness')
        super(Sony, self)._set_endian(endian)
        self._SonyPropDesc = self._SonyPropDesc()

    def event(self, wait=False):
        '''Check Sony or PTP events

        If `wait` this function is blocking. Otherwise it may return None.
        '''
        evt = super(Sony, self).event(wait=wait)
        return evt

    def get_device_info(self):
        logger.debug('Sony get_device_info')
        di = super(Sony, self).get_device_info()
        try:
            if (
                    hasattr(di, 'OperationsSupported') and
                    'SDIOConnect' in di.OperationsSupported
            ):
                with self.session():
                    self.sdio_connect(1)
                    self.sdio_connect(2)
                    sdi = self.sdio_get_ext_device_info()
                    logger.debug(self._SonyDeviceInfo.parse(sdi.Data[2:]))
                    # TODO: finish Sony property integration

        except Exception as e:
            logger.error(e)
            pass

        return di

    def sdio_connect(self, mode):
        '''Change Sony camera mode'''
        ptp = Container(
            OperationCode='SDIOConnect',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[mode]
        )
        return self.recv(ptp)

    def sdio_get_ext_device_info(self):
        '''Change Sony camera mode'''
        ptp = Container(
            OperationCode='SDIOGetExtDeviceInfo',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[0xFF]  # TODO: Meaning??
        )
        return self.recv(ptp)
