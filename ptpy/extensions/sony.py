'''This module extends PTPDevice for Sony devices.

Use it in a master module that determines the vendor and automatically uses its
extension. This is why inheritance is not explicit.
'''
from contextlib import contextmanager
from construct import Container, Struct, Range, Computed, Enum, Array, PrefixedArray
from ..ptp import PTPError
import logging
logger = logging.getLogger(__name__)

__all__ = ('Sony',)


class SonyError(PTPError):
    pass


class Sony(object):
    '''This class implements Sony's PTP operations.'''
    def __init__(self, *args, **kwargs):
        logger.debug('Init Sony')
        super(Sony, self).__init__(*args, **kwargs)
        # TODO: expose the choice to disable automatic Sony extension
        self.__raw = False

    @contextmanager
    def session(self):
        '''
        Manage Sony session with context manager.
        '''
        # When raw device, do not perform
        if self.__raw:
            with super(Sony, self).session():
                yield
            return

        with super(Sony, self).session():
            logger.debug('Authentication')
            r = []
            r.append(self.sdio_connect(1))
            r.append(self.sdio_connect(2))
            r.append(self.sdio_get_ext_device_info())
            r.append(self.sdio_connect(3))

            if not all(map(lambda r: r.ResponseCode == 'OK', r)):
                raise SonyError('Could not authenticate')
            else:
                logger.debug('Authentication done')
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
        return Range(0, 2, self._PTPArray(self._PropertyCode))

    def _Visibility(self):
        return Enum(
            self._UInt8,
            Disabled=0x00,
            Enabled=0x01,
            DisplayOnly=0x02,
        )

    def _SonyPropDesc(self):
        return Struct(
            'PropertyCode' / self._PropertyCode,
            'DataTypeCode' / self._DataTypeCode,
            'SonyGetSet' / self._UInt8,
            'GetSet' / Computed(
                lambda x: 'GetSet' if x.SonyGetSet & 0x01 else 'Get'
            ),
            'Visibility' / self._Visibility,
            'FactoryDefaultValue' / self._DataType,
            'CurrentValue' / self._DataType,
            'FormFlag' / self._FormFlag,
            'Form' / self._Form(self._DataType)
        )

    def _SonyAllPropDesc(self):
        return PrefixedArray(self._UInt64, self._SonyPropDesc)

    def _ExposureProgramMode(self):
        return Enum(
            self._UInt16,
            IntelligentAuto=0x8000,
            SuperiorAuto=0x8001,
            P=0x2,
            A=0x3,
            S=0x4,
            M=0x1,
            MovieP=0x8050,
            MovieA=0x8051,
            MovieS=0x8052,
            MovieM=0x8053,
            # Mode=0x8054, # TODO: ??
            Panoramic=0x8041,
            Portrait=0x7,
            SportsAction=0x8011,
            Macro=0x8015,
            Landscape=0x8014,
            Sunset=0x8012,
            NightScene=0x8013,
            HandheldTwilight=0x8016,
            NightPortrait=0x8017,
            AntiMotionBlur=0x8018,
        )

    def _set_endian(self, endian):
        logger.debug('Set Sony endianness')
        super(Sony, self)._set_endian(endian)
        self._ExposureProgramMode = self._ExposureProgramMode()
        self._Visibility = self._Visibility()
        self._SonyPropDesc = self._SonyPropDesc()
        self._SonyDeviceInfo = self._SonyDeviceInfo()
        self._SonyAllPropDesc = self._SonyAllPropDesc()

    def event(self, wait=False):
        '''Check Sony or PTP events

        If `wait` this function is blocking. Otherwise it may return None.
        '''
        evt = super(Sony, self).event(wait=wait)
        return evt

    def sdio_connect(self, step, key1=0, key2=0):
        '''Authentication handshake'''
        ptp = Container(
            OperationCode='SDIOConnect',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[step, key1, key2]
        )
        return self.recv(ptp)

    def sdio_get_ext_device_info(self, version=0xc8):
        '''Sony DeviceInfo'''
        ptp = Container(
            OperationCode='SDIOGetExtDeviceInfo',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[version]
        )
        return self.recv(ptp)

    def get_all_device_prop_data(self):
        ptp = Container(
            OperationCode='GetAllDevicePropData',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._SonyAllPropDesc)

    def set_control_device_A(self, device_property, value_payload):
        code = self._code(device_property, self._PropertyCode)
        ptp = Container(
            OperationCode='SetControlDeviceA',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[code]
        )
        response = self.send(ptp, value_payload)
        return response

    def set_control_device_B(self, device_property, value_payload):
        code = self._code(device_property, self._PropertyCode)
        ptp = Container(
            OperationCode='SetControlDeviceB',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[code]
        )
        response = self.send(ptp, value_payload)
        return response

    def get_control_device_desc(self, device_property):
        code = self._code(device_property, self._PropertyCode)
        ptp = Container(
            OperationCode='GetControlDeviceDesc',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[code]
        )
        response = self.recv(ptp)
        return response
