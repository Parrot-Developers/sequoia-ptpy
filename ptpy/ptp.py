'''This module implements Picture Transfer Protocol (ISO 15740:2013(E))

It is transport agnostic and requires a transport layer to provide the missing
methods in the class :py:class`PTPDevice`.

Convenience structures are provided to pack messages. These are native-endian
and may need to be adapted to transport-endianness by calling
`_set_endian(endianness)` where `endianness` can be `'big'`, `'little'` or
`'native'`.
'''
from construct import (
    Array, BitsInteger, Computed, Container, Enum, ExprAdapter, Int16sb,
    Int16sl, Int16sn, Int16ub, Int16ul, Int16un, Int32sb, Int32sl, Int32sn,
    Int32ub, Int32ul, Int32un, Int64sb, Int64sl, Int64sn, Int64ub, Int64ul,
    Int64un, Int8sb, Int8sl, Int8sn, Int8ub, Int8ul, Int8un, Pass,
    PrefixedArray, Struct, Switch,
    )
from contextlib import contextmanager
from dateutil.parser import parse as iso8601
from datetime import datetime
import logging
import six

logger = logging.getLogger(__name__)

# Module specific
# _______________
__all__ = ('PTPError', 'PTPUnimplemented', 'PTP',)
__author__ = 'Luis Mario Domenzain'


# Exceptions
# ----------
class PTPError(Exception):
    '''PTP implementation exceptions.'''
    pass


class PTPUnimplemented(PTPError):
    '''Exception to indicate missing implementation.'''
    pass


class PTP(object):
    '''Implement bare PTP device. Vendor specific devices should extend it.'''
    # Base PTP protocol transaction elements
    # --------------------------------------
    _UInt8 = Int8un
    _UInt16 = Int16un
    _UInt32 = Int32un
    _UInt64 = Int64un
    _UInt128 = BitsInteger(128)

    _Int8 = Int8sn
    _Int16 = Int16sn
    _Int32 = Int32sn
    _Int64 = Int64sn
    _Int128 = BitsInteger(128, signed=True)

    def _Parameter(self):
        '''Return desired endianness for Parameter'''
        return self._UInt32

    def _SessionID(self):
        '''Return desired endianness for SessionID'''
        return self._UInt32

    def _TransactionID(self):
        '''Return desired endianness for TransactionID'''
        return Enum(
            self._UInt32,
            default=Pass,
            NA=0xFFFFFFFF,
        )

    # TODO: Check if these Enums can be replaced with more general
    # associations. Or even with Python Enums. Otherwise there is always a risk
    # of a typo creeping in.
    def _OperationCode(self, **vendor_operations):
        '''Return desired endianness for known OperationCode'''
        return Enum(
            self._UInt16,
            default=Pass,
            Undefined=0x1000,
            GetDeviceInfo=0x1001,
            OpenSession=0x1002,
            CloseSession=0x1003,
            GetStorageIDs=0x1004,
            GetStorageInfo=0x1005,
            GetNumObjects=0x1006,
            GetObjectHandles=0x1007,
            GetObjectInfo=0x1008,
            GetObject=0x1009,
            GetThumb=0x100A,
            DeleteObject=0x100B,
            SendObjectInfo=0x100C,
            SendObject=0x100D,
            InitiateCapture=0x100E,
            FormatStore=0x100F,
            ResetDevice=0x1010,
            SelfTest=0x1011,
            SetObjectProtection=0x1012,
            PowerDown=0x1013,
            GetDevicePropDesc=0x1014,
            GetDevicePropValue=0x1015,
            SetDevicePropValue=0x1016,
            ResetDevicePropValue=0x1017,
            TerminateOpenCapture=0x1018,
            MoveObject=0x1019,
            CopyObject=0x101A,
            GetPartialObject=0x101B,
            InitiateOpenCapture=0x101C,
            StartEnumHandles=0x101D,
            EnumHandles=0x101E,
            StopEnumHandles=0x101F,
            GetVendorExtensionMapss=0x1020,
            GetVendorDeviceInfo=0x1021,
            GetResizedImageObject=0x1022,
            GetFilesystemManifest=0x1023,
            GetStreamInfo=0x1024,
            GetStream=0x1025,
            **vendor_operations
            )

    def _ResponseCode(self, **vendor_responses):
        '''Return desired endianness for known ResponseCode'''
        return Enum(
            self._UInt16,
            default=Pass,
            Undefined=0x2000,
            OK=0x2001,
            GeneralError=0x2002,
            SessionNotOpen=0x2003,
            InvalidTransactionID=0x2004,
            OperationNotSupported=0x2005,
            ParameterNotSupported=0x2006,
            IncompleteTransfer=0x2007,
            InvalidStorageId=0x2008,
            InvalidObjectHandle=0x2009,
            DevicePropNotSupported=0x200A,
            InvalidObjectFormatCode=0x200B,
            StoreFull=0x200C,
            ObjectWriteProtected=0x200D,
            StoreReadOnly=0x200E,
            AccessDenied=0x200F,
            NoThumbnailPresent=0x2010,
            SelfTestFailed=0x2011,
            PartialDeletion=0x2012,
            StoreNotAvailable=0x2013,
            SpecificationByFormatUnsupported=0x2014,
            NoValidObjectInfo=0x2015,
            InvalidCodeFormat=0x2016,
            UnknownVendorCode=0x2017,
            CaptureAlreadyTerminated=0x2018,
            DeviceBusy=0x2019,
            InvalidParentObject=0x201A,
            InvalidDevicePropFormat=0x201B,
            InvalidDevicePropValue=0x201C,
            InvalidParameter=0x201D,
            SessionAlreadyOpened=0x201E,
            TransactionCanceled=0x201F,
            SpecificationOfDestinationUnsupported=0x2020,
            InvalidEnumHandle=0x2021,
            NoStreamEnabled=0x2022,
            InvalidDataset=0x2023,
            **vendor_responses
            )

    def _EventCode(self, **vendor_events):
        '''Return desired endianness for known EventCode'''
        return Enum(
            self._UInt16,
            default=Pass,
            Undefined=0x4000,
            CancelTransaction=0x4001,
            ObjectAdded=0x4002,
            ObjectRemoved=0x4003,
            StoreAdded=0x4004,
            StoreRemoved=0x4005,
            DevicePropChanged=0x4006,
            ObjectInfoChanged=0x4007,
            DeviceInfoChanged=0x4008,
            RequestObjectTransfer=0x4009,
            StoreFull=0x400A,
            DeviceReset=0x400B,
            StorageInfoChanged=0x400C,
            CaptureComplete=0x400D,
            UnreportedStatus=0x400E,
            **vendor_events
            )

    def _Event(self):
        return Struct(
            'EventCode' / self._EventCode,
            'SessionID' / self._SessionID,
            'TransactionID' / self._TransactionID,
            'Parameter' / Array(3, self._Parameter),
        )

    def _Response(self):
        return Struct(
            'ResponseCode' / self._ResponseCode,
            'SessionID' / self._SessionID,
            'TransactionID' / self._TransactionID,
            'Parameter' / Array(5, self._Parameter),
        )

    def _Operation(self):
        return Struct(
            'OperationCode' / self._OperationCode,
            'SessionID' / self._SessionID,
            'TransactionID' / self._TransactionID,
            'Parameter' / Array(5, self._Parameter),
        )

    def _PropertyCode(self, **vendor_properties):
        '''Return desired endianness for known OperationCode'''
        return Enum(
            self._UInt16,
            default=Pass,
            Undefined=0x5000,
            BatteryLevel=0x5001,
            FunctionalMode=0x5002,
            ImageSize=0x5003,
            CompressionSetting=0x5004,
            WhiteBalance=0x5005,
            RGBGain=0x5006,
            FNumber=0x5007,
            FocalLength=0x5008,
            FocusDistance=0x5009,
            FocusMode=0x500A,
            ExposureMeteringMode=0x500B,
            FlashMode=0x500C,
            ExposureTime=0x500D,
            ExposureProgramMode=0x500E,
            ExposureIndex=0x500F,
            ExposureBiasCompensation=0x5010,
            DateTime=0x5011,
            CaptureDelay=0x5012,
            StillCaptureMode=0x5013,
            Contrast=0x5014,
            Sharpness=0x5015,
            DigitalZoom=0x5016,
            EffectMode=0x5017,
            BurstNumber=0x5018,
            BurstInterval=0x5019,
            TimelapseNumber=0x501A,
            TimelapseInterval=0x501B,
            FocusMeteringMode=0x501C,
            UploadURL=0x501D,
            Artist=0x501E,
            CopyrightInfo=0x501F,
            **vendor_properties
        )

    # PTP Datasets for specific operations
    # ------------------------------------
    def _ObjectHandle(self):
        '''Return desired endianness for ObjectHandle'''
        return self._UInt32

    def _ObjectFormatCode(self, **vendor_object_formats):
        '''Return desired endianness for known ObjectFormatCode'''
        return Enum(
            self._UInt16,
            default=Pass,
            # Ancilliary
            UndefinedAncilliary=0x3000,
            Association=0x3001,
            Script=0x3002,
            Executable=0x3003,
            Text=0x3004,
            HTML=0x3005,
            DPOF=0x3006,
            AIFF=0x3007,
            WAV=0x3008,
            MP3=0x3009,
            AVI=0x300A,
            MPEG=0x300B,
            ASF=0x300C,
            QT=0x300D,
            # Images
            UndefinedImage=0x3800,
            EXIF_JPEG=0x3801,
            TIFF_EP=0x3802,
            FlashPix=0x3803,
            BMP=0x3804,
            CIFF=0x3805,
            GIF=0x3807,
            JFIF=0x3808,
            PCD=0x3809,
            PICT=0x380A,
            PNG=0x380B,
            TIFF=0x380D,
            TIFF_IT=0x380E,
            JP2=0x380F,
            JPX=0x3810,
            DNG=0x3811,
            **vendor_object_formats
        )

    def _DateTime(self):
        '''Return desired endianness for DateTime'''
        return ExprAdapter(
            self._PTPString,
            encoder=lambda obj, ctx:
                # TODO: Support timezone encoding.
                datetime.strftime(obj, '%Y%m%dT%H%M%S.%f')[:-5],
            decoder=lambda obj, ctx: iso8601(obj),
        )

    def _PTPString(self):
        '''Returns a PTP String constructor'''
        return ExprAdapter(
            PrefixedArray(self._UInt8, self._UInt16),
            encoder=lambda obj, ctx:
                [] if len(obj) == 0 else [ord(c) for c in six.text_type(obj)]+[0],
            decoder=lambda obj, ctx:
                u''.join(
                [six.unichr(o) for o in obj]
                ).split('\x00')[0],
            )

    def _PTPArray(self, element):
        return PrefixedArray(self._UInt32, element)

    def _VendorExtensionID(self):
        return Enum(
            self._UInt32,
            default=Pass,
            EastmanKodak=0x00000001,
            SeikoEpson=0x00000002,
            Agilent=0x00000003,
            Polaroid=0x00000004,
            AgfaGevaert=0x00000005,
            Microsoft=0x00000006,
            Equinox=0x00000007,
            Viewquest=0x00000008,
            STMicroelectronics=0x00000009,
            Nikon=0x0000000A,
            Canon=0x0000000B,
            FotoNation=0x0000000C,
            PENTAX=0x0000000D,
            Fuji=0x0000000E,
            Sony=0x00000011,  # Self-imposed.
            NDD=0x00000012,  # ndd Medical Technologies
            Samsung=0x0000001A,
            Parrot=0x0000001B,
            Panasonic=0x0000001C,
        )

    def _DeviceInfo(self):
        '''Return desired endianness for DeviceInfo'''
        return Struct(
            'StandardVersion' / self._UInt16,
            'VendorExtensionID' / self._VendorExtensionID,
            'VendorExtensionVersion' / self._UInt16,
            'VendorExtensionDesc' / self._PTPString,
            'FunctionalMode' / self._UInt16,
            'OperationsSupported' / self._PTPArray(self._OperationCode),
            'EventsSupported' / self._PTPArray(self._EventCode),
            'DevicePropertiesSupported' / self._PTPArray(self._PropertyCode),
            'CaptureFormats' / self._PTPArray(self._ObjectFormatCode),
            'ImageFormats' / self._PTPArray(self._ObjectFormatCode),
            'Manufacturer' / self._PTPString,
            'Model' / self._PTPString,
            'DeviceVersion' / self._PTPString,
            'SerialNumber' / self._PTPString,
        )

    def _StorageType(self):
        '''Return desired endianness for StorageType'''
        return Enum(
            self._UInt16,
            default=Pass,
            Undefined=0x0000,
            FixedROM=0x0001,
            RemovableROM=0x0002,
            FixedRAM=0x0003,
            RemovableRAM=0x0004,
        )

    def _FilesystemType(self, **vendor_filesystem_types):
        '''Return desired endianness for known FilesystemType'''
        return Enum(
            self._UInt16,
            default=Pass,
            Undefined=0x0000,
            GenericFlat=0x0001,
            GenericHierarchical=0x0002,
            DCF=0x0003,
            **vendor_filesystem_types
        )

    def _AccessCapability(self):
        '''Return desired endianness for AccessCapability'''
        return Enum(
            self._UInt16,
            default=Pass,
            ReadWrite=0x0000,
            ReadOnlyWithoutObjectDeletion=0x0001,
            ReadOnlyWithObjectDeletion=0x0002,
        )

    def _StorageInfo(self):
        '''Return desired endianness for StorageInfo'''
        return Struct(
            'StorageType' / self._StorageType,
            'FilesystemType' / self._FilesystemType,
            'AccessCapability' / self._AccessCapability,
            'MaxCapacity' / self._UInt64,
            'FreeSpaceInBytes' / self._UInt64,
            'FreeSpaceInImages' / self._UInt32,
            'StorageDescription' / self._PTPString,
            'VolumeLabel' / self._PTPString,
        )

    def _StorageID(self):
        '''Return desired endianness for StorageID'''
        # TODO: automatically set and parse PhysicalID and LogicalID
        return self._UInt32

    def _StorageIDs(self):
        '''Return desired endianness for StorageID'''
        # TODO: automatically set and parse PhysicalID and LogicalID
        return self._PTPArray(self._StorageID)

    def _DataTypeCode(self, **vendor_datatype_codes):
        '''Return desired endianness for DevicePropDesc'''
        return Enum(
            self._UInt16,
            default=Pass,
            Undefined=0x0000,
            Int128=0x0009,
            Int128Array=0x4009,
            Int16=0x0003,
            Int16Array=0x4003,
            Int32=0x0005,
            Int32Array=0x4005,
            Int64=0x0007,
            Int64Array=0x4007,
            Int8=0x0001,
            Int8Array=0x4001,
            UInt128=0x000a,
            UInt128Array=0x400a,
            UInt16=0x0004,
            UInt16Array=0x4004,
            UInt32=0x0006,
            UInt32Array=0x4006,
            UInt64=0x0008,
            UInt64Array=0x4008,
            UInt8=0x0002,
            UInt8Array=0x4002,
            String=0xFFFF,
            **vendor_datatype_codes
        )

    def _DataType(self, **vendor_datatypes):
        datatypes = {
            'Int128': self._Int128,
            'Int128Array': self._PTPArray(self._Int128),
            'Int16': self._Int16,
            'Int16Array': self._PTPArray(self._Int16),
            'Int32': self._Int32,
            'Int32Array': self._PTPArray(self._Int32),
            'Int64': self._Int64,
            'Int64Array': self._PTPArray(self._Int64),
            'Int8': self._Int8,
            'Int8Array': self._PTPArray(self._Int8),
            'UInt128': self._UInt128,
            'UInt128Array': self._PTPArray(self._UInt128),
            'UInt16': self._UInt16,
            'UInt16Array': self._PTPArray(self._UInt16),
            'UInt32': self._UInt32,
            'UInt32Array': self._PTPArray(self._UInt32),
            'UInt64': self._UInt64,
            'UInt64Array': self._PTPArray(self._UInt64),
            'UInt8': self._UInt8,
            'UInt8Array': self._PTPArray(self._UInt8),
            'String': self._PTPString,
        }
        datatypes.update(vendor_datatypes if vendor_datatypes else {})

        def DataTypeCode(ctx):
            # Try to get the DataTypeCode from the parent contexts up to 20
            # levels...
            for i in range(20):
                try:
                    return ctx.DataTypeCode
                except AttributeError:
                    ctx = ctx._

        return Switch(
            DataTypeCode,
            datatypes,
            default=Pass
        )

    def _GetSet(self):
        return Enum(
            self._UInt8,
            default=Pass,
            Get=0x00,
            GetSet=0x01,
        )

    def _FormFlag(self):
        return Enum(
            self._UInt8,
            default=Pass,
            NoForm=0x00,
            Range=0x01,
            Enumeration=0x02,
        )

    def _RangeForm(self, element):
        return Struct(
                'MinimumValue' / element,
                'MaximumValue' / element,
                'StepSize' / element,
            )

    def _EnumerationForm(self, element):
        return PrefixedArray(self._UInt16, element)

    def _Form(self, element):
        return Switch(
            lambda x: x.FormFlag,
            {
                'Range': 'Range' / self._RangeForm(element),
                'Enumeration': 'Enumeration' / self._EnumerationForm(element),
                'NoForm': Pass
            },
            default=Pass,
        )

    def _DevicePropDesc(self):
        '''Return desired endianness for DevicePropDesc'''
        return Struct(
            'PropertyCode' / self._PropertyCode,
            'DataTypeCode' / self._DataTypeCode,
            'GetSet' / self._GetSet,
            'FactoryDefaultValue' / self._DataType,
            'CurrentValue' / self._DataType,
            'FormFlag' / self._FormFlag,
            'Form' / self._Form(self._DataType)
        )

    def _ProtectionStatus(self):
        return Enum(
            self._UInt16,
            default=Pass,
            NoProtection=0x0000,
            ReadOnly=0x0001,
        )

    def _AssociationType(self, **vendor_associations):
        return Enum(
            self._UInt16,
            default=Pass,
            Undefined=0x0000,
            GenericFolder=0x0001,
            Album=0x0002,
            TimeSequence=0x0003,
            HorizontalPanoramic=0x0004,
            VerticalPanoramic=0x0005,
            Panoramic2D=0x0006,
            AncillaryData=0x0007,
            **vendor_associations
        )

    def _AssociationDesc(self, **vendor_associations):
        return Enum(
            self._UInt32,
            default=Pass,
            Undefined=0x00000000,
            DefaultPlaybackData=0x00000003,
            ImagesPerRow=0x00000006,
            **vendor_associations
        )

    def _ObjectInfo(self):
        '''Return desired endianness for ObjectInfo'''
        return Struct(
            'StorageID' / self._StorageID,
            'ObjectFormat' / self._ObjectFormatCode,
            'ProtectionStatus' / self._ProtectionStatus,
            'ObjectCompressedSize' / self._UInt32,
            'ThumbFormat' / self._ObjectFormatCode,
            'ThumbCompressedSize' / self._UInt32,
            'ThumbPixWidth' / self._UInt32,
            'ThumbPixHeight' / self._UInt32,
            'ImagePixWidth' / self._UInt32,
            'ImagePixHeight' / self._UInt32,
            'ImageBitDepth' / self._UInt32,
            'ParentObject' / self._ObjectHandle,
            'AssociationType' / self._AssociationType,
            'AssociationDesc' / self._AssociationDesc,
            'SequenceNumber' / self._UInt32,
            'Filename' / self._PTPString,
            'CaptureDate' / self._DateTime,
            'ModificationDate' / self._DateTime,
            'Keywords' / self._PTPString,
        )

    def _VendorExtensionMap(self):
        '''Return desired endianness for VendorExtensionMap'''
        # TODO: Integrate vendor extensions and their Enums to parse Native
        # codes to their name.
        return Struct(
            'NativeCode' / self._UInt16,
            'MappedCode' / self._UInt16,
            'MappedVendorExtensionID' / self._VendorExtensionID,
        )

    def _VendorExtensionMapArray(self):
        '''Return desired endianness for VendorExtensionMapArray'''
        return PrefixedArray(
            self._UInt64,
            self._VendorExtensionMap,
        )

    # Helper to concretize generic constructors to desired endianness
    # ---------------------------------------------------------------
    def _set_endian(self, endian, explicit=None):
        '''Instantiate constructors to given endianness'''
        # All constructors need to be instantiated before use by setting their
        # endianness. But only those that don't depend on endian-generic
        # constructors need to be explicitly instantiated to a given
        # endianness.
        logger.debug('Set PTP endianness')
        if endian == 'little':
            self._UInt8 = Int8ul
            self._UInt16 = Int16ul
            self._UInt32 = Int32ul
            self._UInt64 = Int64ul
            self._UInt128 = BitsInteger(128, signed=False, swapped=True)
            self._Int8 = Int8sl
            self._Int16 = Int16sl
            self._Int32 = Int32sl
            self._Int64 = Int64sl
            self._Int128 = BitsInteger(128, signed=True, swapped=True)
        elif endian == 'big':
            self._UInt8 = Int8ub
            self._UInt16 = Int16ub
            self._UInt32 = Int32ub
            self._UInt64 = Int64ub
            self._UInt128 = BitsInteger(128, signed=False, swapped=False)
            self._Int8 = Int8sb
            self._Int16 = Int16sb
            self._Int32 = Int32sb
            self._Int64 = Int64sb
            self._Int128 = BitsInteger(128, signed=True, swapped=False)
        elif endian == 'native':
            self._UInt8 = Int8un
            self._UInt16 = Int16un
            self._UInt32 = Int32un
            self._UInt64 = Int64un
            self._UInt128 = BitsInteger(128, signed=False)
            self._Int8 = Int8sn
            self._Int16 = Int16sn
            self._Int32 = Int32sn
            self._Int64 = Int64sn
            self._Int128 = BitsInteger(128, signed=True)
        else:
            raise PTPError(
                'Only little and big endian conventions are supported.'
            )

        if explicit is not None and explicit:
            logger.debug('Initialized explicit constructors only')
            return
        elif explicit is not None and not explicit:
            logger.debug('Initialize implicit constructors')

        # Implicit instantiation. Needs to happen after the above.
        self._PTPString = self._PTPString()
        self._DateTime = self._DateTime()
        self._Parameter = self._Parameter()
        self._VendorExtensionID = self._VendorExtensionID()
        self._OperationCode = self._OperationCode()
        self._EventCode = self._EventCode()
        self._PropertyCode = self._PropertyCode()
        self._ObjectFormatCode = self._ObjectFormatCode()
        self._DeviceInfo = self._DeviceInfo()
        self._SessionID = self._SessionID()
        self._TransactionID = self._TransactionID()
        self._ObjectHandle = self._ObjectHandle()
        self._ResponseCode = self._ResponseCode()
        self._Event = self._Event()
        self._Response = self._Response()
        self._Operation = self._Operation()
        self._StorageID = self._StorageID()
        self._StorageIDs = self._StorageIDs()
        self._StorageType = self._StorageType()
        self._FilesystemType = self._FilesystemType()
        self._AccessCapability = self._AccessCapability()
        self._StorageInfo = self._StorageInfo()
        self._DataTypeCode = self._DataTypeCode()
        self._DataType = self._DataType()
        self._GetSet = self._GetSet()
        self._FormFlag = self._FormFlag()
        self._DevicePropDesc = self._DevicePropDesc()
        self._VendorExtensionMap = self._VendorExtensionMap()
        self._VendorExtensionMapArray = self._VendorExtensionMapArray()

        self._AssociationType = self._AssociationType()
        self._AssociationDesc = self._AssociationDesc()
        self._ProtectionStatus = self._ProtectionStatus()
        self._ObjectInfo = self._ObjectInfo()

    def __init__(self, *args, **kwargs):
        logger.debug('Init PTP')
        # Session and transaction helpers
        # -------------------------------
        self._session = 0
        self.__session_open = False
        self.__transaction_id = 1
        self.__has_the_knowledge = False
        super(PTP, self).__init__(*args, **kwargs)

    @property
    def _transaction(self):
        '''Give magical property for the latest TransactionID'''
        current_id = 0
        if self.__session_open:
            current_id = self.__transaction_id
            self.__transaction_id += 1
            if self.__transaction_id > 0xFFFFFFFE:
                self.__transaction_id = 1
        return current_id

    @_transaction.setter
    def _transaction(self, value):
        '''Manage reset of TransactionID'''
        if value != 1:
            raise PTPError(
                'Current TransactionID should not be set. Only reset.'
            )
        else:
            self.__transaction_id = 1

    @property
    def session_id(self):
        '''Expose internat SessionID'''
        return self._session

    @session_id.setter
    def session_id(self, value):
        '''Ignore external modifications to SessionID'''
        pass

    @contextmanager
    def session(self):
        '''
        Manage session with context manager.

        Once transport specific interfaces are defined, this allows easier,
        more nuclear sessions:

            from ptpy import PTPy
            camera = PTPy()
            with camera.session():
                camera.get_device_info()
        '''
        # TODO: Deal with devices that only support one session (where
        # SessionID must be always 1, like some older Canon cameras.)
        # TODO: Deal with devices that only support one arbitrary session where
        # the ID is communicated to the initiator after an OpenSession attempt.
        # This might also account for the above.
        logger.debug('Session requested')
        if not self.__session_open:
            logger.debug('Open session')
            try:
                self.open_session()
                yield
            finally:
                logger.debug('Close session')
                if self.__session_open:
                    self.close_session()
        else:
            logger.debug('Using outer session')
            yield

    @contextmanager
    def open_capture(self):
        '''
        Manage open capture with context manager.

        This allows easier open capture with automatic closing
        '''
        # TODO: implement!

    # Transport-specific functions
    # ----------------------------
    def send(self, ptp_container, payload):
        '''Operation with dataphase from initiator to responder'''
        try:
            return super(PTP, self).send(ptp_container, payload)
        except Exception as e:
            logger.error(e)
            raise e

    def recv(self, ptp_container):
        '''Operation with dataphase from responder to initiator'''
        try:
            return super(PTP, self).recv(ptp_container)
        except Exception as e:
            logger.error(e)
            raise e

    def mesg(self, ptp_container):
        '''Operation with no dataphase'''
        try:
            return super(PTP, self).mesg(ptp_container)
        except Exception as e:
            logger.error(e)
            raise e

    def event(self, wait=False):
        try:
            return super(PTP, self).event(wait=wait)
        except Exception as e:
            logger.error(e)
            raise e

    # Operation-specific methods and helpers
    # --------------------------------------
    def _parse_if_data(self, response, constructor):
        '''If the response contains data, parse it with constructor.'''
        return (constructor.parse(response.Data)
                if hasattr(response, 'Data') else None)

    def _build_if_not_data(self, data, constructor):
        '''If the data is not binary, build it with constructor.'''
        return (constructor.build(data)
                if isinstance(data, Container) else data)

    def _name(self, name_or_code, constructor):
        '''Helper method to get the code for an Enum constructor.'''
        name = name_or_code
        if isinstance(name_or_code, int):
            try:
                name = constructor.decoding[name_or_code]
            except Exception:
                pass

        return name

    def _code(self, name_or_code, constructor):
        '''Helper method to get the code for an Enum constructor.'''
        if isinstance(name_or_code, six.string_types):
            try:
                code = constructor.encoding[name_or_code]
            except Exception:
                raise PTPError('Unknown property name. Try with a number?')
        else:
            code = name_or_code

        return code

    def _obtain_the_knowledge(self):
        '''Initialise an internal representation of device behaviour.'''
        logger.debug('Gathering info about all device properties')
        self.__device_info = self.get_device_info()
        self.__prop_desc = {}
        with self.session():
            for p in self.__device_info.DevicePropertiesSupported:
                # TODO: Update __prop_desc with arrival of events
                # transparently.
                self.__prop_desc[p] = self.get_device_prop_desc(p)
                # TODO: Get info regarding ObjectHandles here. And update as
                # events are received. This should be transparent for the user.

        self.__has_the_knowledge = True

    def _update_the_knowledge(self, props=None):
        '''Update an internal representation of device behaviour.'''
        logger.debug('Gathering info about extra device properties')
        with self.session():
            for p in props:
                self.__prop_desc[p] = self.get_device_prop_desc()
                self.__device_info.DevicePropertiesSupported.append(p)

    def open_session(self):
        self._session += 1
        self._transaction = 1
        ptp = Container(
            OperationCode='OpenSession',
            # Only the OpenSession operation is allowed to have a 0
            # SessionID, because no session is open yet.
            SessionID=0,
            TransactionID=0,
            Parameter=[self._session]
        )
        response = self.mesg(ptp)
        if response.ResponseCode == 'OK':
            self.__session_open = True
        return response

    def close_session(self):
        ptp = Container(
            OperationCode='CloseSession',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.mesg(ptp)
        if response.ResponseCode == 'OK':
            self.__session_open = False
        return response

    def reset_device(self):
        ptp = Container(
            OperationCode='ResetDevice',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[],
        )
        response = self.recv(ptp)
        if response.ResponseCode == 'OK':
            self.__session_open = False
        return response

    def power_down(self):
        ptp = Container(
            OperationCode='PowerDown',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[],
        )
        response = self.recv(ptp)
        if response.ResponseCode == 'OK':
            self.__session_open = False
        return response

    # TODO: Add decorator to check there is an open session.
    def reset_device_prop_value(self, device_property, reset_all=False):
        '''Reset given device property to factory default.

        If `reset_all` is `True`, the device_property can be `None`.
        '''
        if isinstance(device_property, six.string_types):
            try:
                code = self._PropertyCode.encoding[device_property]
            except Exception:
                raise PTPError('Unknown property name. Try with a number?')
        else:
            code = device_property

        ptp = Container(
            OperationCode='ResetDevicePropValue',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[0xffffffff if reset_all else code],
        )
        response = self.recv(ptp)
        return response

    def get_device_info(self):
        ptp = Container(
            OperationCode='GetDeviceInfo',
            SessionID=self._session,
            # GetrDeviceInfo can happen outside a session. But if there is one
            # running just use that one.
            TransactionID=(self._transaction if self.__session_open else 0),
            Parameter=[]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._DeviceInfo)

    def get_storage_ids(self):
        ptp = Container(
            OperationCode='GetStorageIDs',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._StorageIDs)

    def get_storage_info(self, storage_id):
        ptp = Container(
            OperationCode='GetStorageInfo',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[storage_id]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._StorageInfo)

    def get_num_objects(
            self,
            storage_id,
            object_format=0,
            object_handle=0,
            all_storage_ids=False,
            all_formats=False,
            in_root=False,
    ):
        '''Total number of objects present in `storage_id`'''
        if object_handle != 0 and in_root and object_handle != 0xffffffff:
            raise ValueError(
                'Cannot get both root and {}'.format(object_handle)
            )
        code = self._code(object_format, self._ObjectFormatCode)
        ptp = Container(
            OperationCode='GetNumObjects',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[
                0xffffffff if all_storage_ids else storage_id,
                0xffffffff if all_formats else code,
                0xffffffff if in_root else object_handle
            ]
        )
        response = self.recv(ptp)
        return response.Parameter[0] if response.Parameter else None

    def get_object_handles(
            self,
            storage_id,
            object_format=0,
            object_handle=0,
            all_storage_ids=False,
            all_formats=False,
            in_root=False,
    ):
        '''Return array of ObjectHandles present in `storage_id`'''
        if object_handle != 0 and in_root and object_handle != 0xffffffff:
            raise ValueError(
                'Cannot get both root and {}'.format(object_handle)
            )
        code = self._code(object_format, self._ObjectFormatCode)
        ptp = Container(
            OperationCode='GetObjectHandles',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[
                0xffffffff if all_storage_ids else storage_id,
                0xffffffff if all_formats else code,
                0xffffffff if in_root else object_handle
            ]
        )
        response = self.recv(ptp)
        return self._parse_if_data(
            response,
            self._PTPArray(self._ObjectHandle)
        )

    def __constructor(self, device_property):
        '''Get the correct constructor using the latest GetDevicePropDesc.'''
        builder = Struct(
            'DataTypeCode' / Computed(
                lambda ctx: self.__prop_desc[device_property].DataTypeCode
            ),
            'Value' / self._DataType
        )
        return builder

    def get_device_prop_desc(self, device_property):
        '''Retrieve the property description.

        Accepts a property name or a number.
        '''
        code = self._code(device_property, self._PropertyCode)

        ptp = Container(
            OperationCode='GetDevicePropDesc',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[code]
        )
        response = self.recv(ptp)
        result = self._parse_if_data(response, self._DevicePropDesc)
        # Update the knowledge on response.
        if self.__has_the_knowledge and hasattr(response, 'Data'):
            device_property = self._name(device_property, self._PropertyCode)
            logger.debug(
                'Updating knowledge of {}'
                .format(
                    hex(device_property)
                    if isinstance(device_property, int) else device_property
                )
            )
            self.__prop_desc[device_property] = result
        return result

    def get_device_prop_value(self, device_property):
        code = self._code(device_property, self._PropertyCode)

        ptp = Container(
            OperationCode='GetDevicePropValue',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[code],
        )
        response = self.recv(ptp)
        if self.__has_the_knowledge and hasattr(response, 'Data'):
            device_property = self._name(device_property, self._PropertyCode)
            c = self.__constructor(device_property)
            response = c.parse(response.Data).Value
        return response

    def set_device_prop_value(self, device_property, value_payload):
        code = self._code(device_property, self._PropertyCode)

        # Attempt to use current knowledge of properties
        if self.__has_the_knowledge:
            device_property = self._name(device_property, self._PropertyCode)
            c = self.__constructor(device_property)
            value_payload = c.build(
                Container(
                    Value=value_payload,
                    DataTypeCode=(
                        self.__prop_desc[device_property].DataTypeCode
                    )
                )
            )

        ptp = Container(
            OperationCode='SetDevicePropValue',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[code],
        )
        response = self.send(ptp, value_payload)
        return response

    def initiate_capture(self, storage_id=0, object_format=0):
        '''Initiate capture with current camera settings.'''
        code = self._code(object_format, self._ObjectFormatCode)
        ptp = Container(
            OperationCode='InitiateCapture',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[
                storage_id,
                code,
            ]
        )
        response = self.recv(ptp)
        return response

    def initiate_open_capture(self, storage_id=0, object_format=0):
        '''Initiate open capture in `storage_id` of type `object_format`.'''
        code = self._code(object_format, self._ObjectFormatCode)
        ptp = Container(
            OperationCode='InitiateOpenCapture',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[
                storage_id,
                code,
            ]
        )
        response = self.recv(ptp)
        return response

    def terminate_open_capture(self, transaction_id):
        '''Terminate the open capture initiated in `transaction_id`'''
        ptp = Container(
            OperationCode='TerminateOpenCapture',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[
                transaction_id,
            ]
        )
        response = self.recv(ptp)
        return response

    def get_object_info(self, handle):
        '''Get ObjectInfo dataset for given handle.'''
        ptp = Container(
            OperationCode='GetObjectInfo',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[handle]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._ObjectInfo)

    def send_object_info(self, objectinfo):
        '''Send ObjectInfo to responder.

        The object should correspond to the latest SendObjectInfo interaction
        between Initiator and Responder.
        '''
        objectinfo = self._build_if_not_data(objectinfo, self._ObjectInfo)

        ptp = Container(
            OperationCode='SendObjectInfo',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )

        return self.send(ptp, objectinfo)

    def send_object(self, bytes_data):
        '''Send object to responder.

        The object should correspond to the latest SendObjectInfo interaction
        between Initiator and Responder.
        '''
        ptp = Container(
            OperationCode='SendObject',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.send(ptp, bytes_data)
        if response.ResponseCode != 'OK':
            response = self.send(ptp, bytes_data)
        return response

    def get_object(self, handle):
        '''Retrieve object from responder.

        The object should correspond to a previous GetObjectInfo interaction
        between Initiator and Responder in the same session.
        '''
        ptp = Container(
            OperationCode='GetObject',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[handle]
        )
        return self.recv(ptp)

    def get_partial_object(self, handle, offset, max_bytes, until_end=False):
        '''Retrieve partial object from responder.

        The object should correspond to a previous GetObjectInfo interaction
        between Initiator and Responder in the same session.
        Size fields represent maximum size as opposed to the actual size.

        The first response parameter represents the actual number of bytes sent
        by responder.
        '''
        ptp = Container(
            OperationCode='GetPartialObject',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[handle,
                       offset,
                       0xFFFFFFFF if until_end else max_bytes]
        )
        return self.recv(ptp)

    def delete_object(
            self,
            handle,
            object_format=0,
            delete_all=False,
            delete_all_images=False
    ):
        '''Delete object for given handle.

        Optionally delete all objects or all images.
        '''
        code = self._code(object_format, self._ObjectFormatCode)

        # Do the most destruction:
        if delete_all and delete_all_images:
            delete_all_images = False

        ptp = Container(
            OperationCode='DeleteObject',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[
                0xFFFFFFFF if delete_all else handle,
                code,
            ]
        )

        return self.mesg(ptp)

    def move_object(
            self,
            handle,
            storage_id=0,
            parent_handle=0,
    ):
        '''Move object to parent.

        Parent should be an Association. Default parent is the root directory
        of `storage_id`
        '''
        ptp = Container(
            OperationCode='MoveObject',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[
                handle,
                storage_id,
                parent_handle,
            ]
        )

        return self.mesg(ptp)

    def copy_object(
            self,
            handle,
            storage_id=0,
            parent_handle=0,
    ):
        '''Copy object to parent.

        Parent should be an Association. Default parent is the root directory
        of `storage_id`
        '''
        ptp = Container(
            OperationCode='CopyObject',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[
                handle,
                storage_id,
                parent_handle,
            ]
        )

        return self.mesg(ptp)

    def get_thumb(self, handle):
        '''Retrieve thumbnail for object from responder.
        '''
        ptp = Container(
            OperationCode='GetThumb',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[handle]
        )
        return self.recv(ptp)

    def get_resized_image_object(self, handle, width, height=0):
        '''Retrieve resized image object from responder.

        The object should correspond to a previous GetObjectInfo interaction
        between Initiator and Responder in the same session.

        If width is provided then the aspect ratio may change. The device may
        not support this.
        '''
        ptp = Container(
            OperationCode='GetResizedImageObject',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[handle, width, height]
        )
        return self.recv(ptp)

    def get_vendor_extension_maps(self, handle):
        '''Get VendorExtension maps when supporting more than one extension.
        '''
        ptp = Container(
            OperationCode='GetVendorExtensionMaps',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        return self._parse_if_data(
            response,
            self._VendorExtensionMapArray)

    def get_vendor_device_info(self, extension):
        '''Get VendorExtension maps when supporting more than one extension.
        '''
        code = self._code(extension, self._VendorExtensionID)
        ptp = Container(
            OperationCode='GetVendorDeviceInfo',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[code]
        )
        response = self.recv(ptp)
        return self._parse_if_data(
            response,
            self._DeviceInfo)

    # TODO: Implement automatic event management.
