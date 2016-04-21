'''This module implements Picture Transfer Protocol (ISO 15740:2013(E))

It is transport agnostic and requires a transport layer to provide the missing
methods in the class :py:class`PTPDevice`.

Convenience structures are provided to pack messages. These are native-endian
and may need to be adapted to transport-endianness:

    SessionID()  # returns native endian constructor
    SessionID(le=True)  # returns little endian constructor
    SessionID(be=True)  # returns big endian constructor
'''
from construct import (
    Container, Array, BitField, Embedded, Enum, ExprAdapter,
    LengthValueAdapter, Pass, PrefixedArray, Rename, Sequence, Struct, Switch,
    UBInt16, UBInt32, UBInt8, ULInt16, ULInt32, ULInt8, UNInt16, UNInt32,
    UNInt8, UBInt64, ULInt64, UNInt64, SLInt8, SLInt16, SLInt32,
    SLInt64, SBInt8, SBInt16, SBInt32, SBInt64, SNInt8, SNInt16, SNInt32,
    SNInt64
    )
from contextlib import contextmanager
from dateutil.parser import parse as iso8601
from datetime import datetime

# Module specific
# _______________
__all__ = ('PTPError', 'PTPUnimplemented', 'PTPDevice',)

__author__ = 'Luis Mario Domenzain'


# Exceptions
# ----------
class PTPError(Exception):
    '''PTP implementation exceptions.'''
    pass


class PTPUnimplemented(PTPError):
    '''Exception to indicate missing implementation.'''
    pass


# Helper functions
# ----------------
def switch_endian(le, be, l, b, n):
    '''Return little, native or big endian.'''
    if (be != le):
        return l if le else b
    elif le:
        raise PTPError('Cannot be both little and big endian...')
    else:
        return n


class PTPDevice(object):
    '''Implement bare PTP Device. Vendor specific devices should extend it.'''

    # Base PTP protocol transaction elements
    # --------------------------------------
    def _UInt8(self, _le_=False, _be_=False):
        return switch_endian(_le_, _be_, ULInt8, UBInt8, UNInt8)

    def _UInt16(self, _le_=False, _be_=False):
        return switch_endian(_le_, _be_, ULInt16, UBInt16, UNInt16)

    def _UInt32(self, _le_=False, _be_=False):
        return switch_endian(_le_, _be_, ULInt32, UBInt32, UNInt32)

    def _UInt64(self, _le_=False, _be_=False):
        return switch_endian(_le_, _be_, ULInt64, UBInt64, UNInt64)

    def _UInt128(self, _le_=False, _be_=False):
        return switch_endian(
            _le_,
            _be_,
            lambda name: BitField(name, 128, swapped=True),
            lambda name: BitField(name, 128, swapped=False),
            lambda name: BitField(name, 128)
        )

    def _Int8(self, _le_=False, _be_=False):
        return switch_endian(_le_, _be_, SLInt8, SBInt8, SNInt8)

    def _Int16(self, _le_=False, _be_=False):
        return switch_endian(_le_, _be_, SLInt16, SBInt16, SNInt16)

    def _Int32(self, _le_=False, _be_=False):
        return switch_endian(_le_, _be_, SLInt32, SBInt32, SNInt32)

    def _Int64(self, _le_=False, _be_=False):
        return switch_endian(_le_, _be_, SLInt64, SBInt64, SNInt64)

    def _Int128(self, _le_=False, _be_=False):
        '''Return desired endianness for Parameter'''
        return switch_endian(
            _le_,
            _be_,
            lambda name: BitField(name, 128, signed=True, swapped=True),
            lambda name: BitField(name, 128, signed=True, swapped=False),
            lambda name: BitField(name, 128, signed=True)
        )

    def _Parameter(self, _le_=False, _be_=False):
        '''Return desired endianness for Parameter'''
        return switch_endian(
            _le_,
            _be_,
            BitField('Parameter', 32, swapped=True),
            BitField('Parameter', 32, swapped=False),
            BitField('Parameter', 32)
        )

    def _SessionID(self):
        '''Return desired endianness for SessionID'''
        return self._UInt32('SessionID')

    def _TransactionID(self):
        '''Return desired endianness for TransactionID'''
        return self._UInt32('TransactionID')

    def _ObjectHandle(self):
        '''Return desired endianness for ObjectHandle'''
        return self._UInt32('ObjectHandle')

    def _DateTime(self):
        '''Return desired endianness for DateTime'''
        return ExprAdapter(
            self._PTPString('DateTime'),
            encoder=lambda obj, ctx:
                # TODO: Support timezone encoding.
                datetime.strftime(obj, '%Y%m%dT%H%M%S.%f')[:-5],
            decoder=lambda obj, ctx: iso8601(obj),
        )

    def _OperationCode(self, **vendor_operations):
        '''Return desired endianness for known OperationCode'''
        return Enum(
            self._UInt16('OperationCode'),
            _default_=Pass,
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
            self._UInt16('ResponseCode'),
            _default_=Pass,
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
            self._UInt16('EventCode'),
            _default_=Pass,
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
            'Event',
            self._EventCode,
            self._SessionID,
            self._TransactionID,
            Array(3, self._Parameter),
        )

    def _Response(self):
        return Struct(
            'Response',
            self._ResponseCode,
            self._SessionID,
            self._TransactionID,
            Array(5, self._Parameter),
        )

    def _Operation(self):
        return Struct(
            'Operation',
            self._OperationCode,
            self._SessionID,
            self._TransactionID,
            Array(5, self._Parameter),
        )

    # PTP Datasets for specific operations
    # ------------------------------------
    def _PropertyCode(self, **vendor_properties):
        '''Return desired endianness for known OperationCode'''
        return Enum(
            self._UInt16('PropertyCode'),
            _default_=Pass,
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

    def _PTPString(self, name):
        '''Returns a PTP String constructor'''
        return ExprAdapter(
            LengthValueAdapter(
                Sequence(
                    name,
                    self._UInt8('NumChars'),
                    Array(lambda ctx: ctx.NumChars, self._UInt16('Chars'))
                )
            ),
            encoder=lambda obj, ctx:
                [] if len(obj) == 0 else [ord(c) for c in unicode(obj)]+[0],
            decoder=lambda obj, ctx:
                u''.join(
                [unichr(o) for o in obj]
                ).split('\x00')[0],
        )

    def _PTPArray(self, name, element):
        return PrefixedArray(
            Rename(name, element),
            length_field=self._UInt32('NumElements'),
        )

    def _ObjectFormatCode(self, **vendor_object_formats):
        '''Return desired endianness for known ObjectFormatCode'''
        return Enum(
            self._UInt16('ObjectFormatCode'),
            # Ancilliary
            Undefined=0x3000,
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
            _default_=Pass,
            **vendor_object_formats
        )

    def _VendorExtensionID(self):
        return Enum(
            self._UInt32('VendorExtensionID'),
            # It seems imaging.org has stopped responding to registry requests
            # and vendors are now just imposing their own...
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
            Samsung=0x0000001A,
            Parrot=0x00000026,  # Self-imposed.
            _default_=Pass,
        )

    def _DeviceInfo(self):
        '''Return desired endianness for DeviceInfo'''
        return Struct(
            'DeviceInfo',
            self._UInt16('StandardVersion'),
            self._VendorExtensionID,
            self._UInt16('VendorExtensionVersion'),
            self._PTPString('VendorExtensionDesc'),
            self._UInt16('FunctionalMode'),
            self._PTPArray('OperationSupported', self._OperationCode),
            self._PTPArray('EventsSupported', self._EventCode),
            self._PTPArray('DevicePropertiesSupported', self._PropertyCode),
            self._PTPArray('CaptureFormats', self._ObjectFormatCode),
            self._PTPArray('ImageFormats', self._ObjectFormatCode),
            self._PTPString('Manufacturer'),
            self._PTPString('Model'),
            self._PTPString('DeviceVersion'),
            self._PTPString('SerialNumber'),
        )

    def _StorageType(self):
        '''Return desired endianness for StorageType'''
        return Enum(
            self._UInt16('StorageType'),
            _default_=Pass,
            Undefined=0x0000,
            FixedROM=0x0001,
            RemovableROM=0x0002,
            FixedRAM=0x0003,
            RemovableRAM=0x0004,
        )

    def _FilesystemType(self, **vendor_filesystem_types):
        '''Return desired endianness for known FilesystemType'''
        return Enum(
            self._UInt16('FilesystemType'),
            _default_=Pass,
            Undefined=0x0000,
            GenericFlat=0x0001,
            GenericHierarchical=0x0002,
            DCF=0x0003,
            **vendor_filesystem_types
        )

    def _AccessCapability(self):
        '''Return desired endianness for AccessCapability'''
        return Enum(
            self._UInt16('AccessCapability'),
            _default_=Pass,
            ReadWrite=0x0000,
            ReadOnlyWithoutObjectDeletion=0x0001,
            ReadOnlyWithObjectDeletion=0x0002,
        )

    def _StorageInfo(self):
        '''Return desired endianness for StorageInfo'''
        return Struct(
            'StorageInfo',
            self._StorageType,
            self._FilesystemType,
            self._AccessCapability,
            self._UInt64('MaxCapacity'),
            self._UInt64('FreeSpaceInBytes'),
            self._UInt32('FreeSpaceInImages'),
            self._PTPString('StorageDescription'),
            self._PTPString('VolumeLabel'),
        )

    def _StorageID(self):
        '''Return desired endianness for StorageID'''
        # TODO: automatically set and parse PhysicalID and LogicalID
        return self._UInt32('StorageID')

    def _StorageIDs(self):
        '''Return desired endianness for StorageID'''
        # TODO: automatically set and parse PhysicalID and LogicalID
        return self._PTPArray('StorageIDs', self._StorageID)

    def _DataTypeCode(self, **vendor_datatype_codes):
        '''Return desired endianness for DevicePropDesc'''
        return Enum(
            self._UInt16('DataTypeCode'),
            _default_=Pass,
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
            'Int128': self._Int128('Int128'),
            'Int128Array': self._PTPArray(
                'Int128Array', self._Int128('Int128')
            ),
            'Int16': self._Int16('Int16'),
            'Int16Array': self._PTPArray(
                'Int16Array', self._Int16('Int16')
            ),
            'Int32': self._Int32('Int32'),
            'Int32Array': self._PTPArray(
                'Int32Array', self._Int32('Int32')
            ),
            'Int64': self._Int64('Int64'),
            'Int64Array': self._PTPArray(
                'Int64Array', self._Int64('Int64')
            ),
            'Int8': self._Int8('Int8'),
            'Int8Array': self._PTPArray(
                'Int8Array', self._Int8('Int8')
            ),
            'UInt128': self._UInt128('UInt128'),
            'UInt128Array': self._PTPArray(
                'UInt128Array', self._UInt128('UInt128')
            ),
            'UInt16': self._UInt16('UInt16'),
            'UInt16Array': self._PTPArray(
                'UInt16Array', self._UInt16('UInt16')
            ),
            'UInt32': self._UInt32('UInt32'),
            'UInt32Array': self._PTPArray(
                'UInt32Array', self._UInt32('UInt32')
            ),
            'UInt64': self._UInt64('UInt64'),
            'UInt64Array': self._PTPArray(
                'UInt64Array', self._UInt64('UInt64')
            ),
            'UInt8': self._UInt8('UInt8'),
            'UInt8Array': self._PTPArray(
                'UInt8Array', self._UInt8('UInt8')
            ),
            'String': self._PTPString('String'),
        }
        datatypes.update(vendor_datatypes if vendor_datatypes else {})
        return Switch(
            'DataType',
            lambda ctx: ctx.DataTypeCode,
            datatypes
        )

    def _GetSet(self):
        return Enum(
            self._UInt8('GetSet'),
            _default_=Pass,
            Get=0x00,
            GetSet=0x01,
        )

    def _FormFlag(self):
        return Enum(
            self._UInt8('FormFlag'),
            _default_=Pass,
            NoForm=0x00,
            Range=0x01,
            Enumeration=0x01,
        )

    def _RangeForm(self, element):
        return Embedded(
            Struct(
                'RangeForm',
                Rename('MinimumValue', element),
                Rename('MaximumValue', element),
                Rename('StepSize', element),
            )
        )

    def _EnumerationForm(self, element):
        return Embedded(
            PrefixedArray(
                Rename('SupportedValues', element),
                length_field=self._UInt16('NumberOfValues'),
            )
        )

    def _Form(self, element):
        return Switch(
            'Form',
            lambda ctx: ctx.FormFlag, {
                'Range': self._RangeForm(element),
                'Enumeration': self._EnumerationForm(element),
            },
            default=Pass,
        )

    def _DevicePropDesc(self):
        '''Return desired endianness for DevicePropDesc'''
        return Struct(
            'DevicePropDesc',
            self._PropertyCode,
            self._DataTypeCode,
            self._GetSet,
            Rename('FactoryDefaultFalue', self._DataType),
            Rename('CurrentValue', self._DataType),
            self._FormFlag,
            self._Form(self._DataType),
        )

    def _ProtectionStatus(self):
        return Enum(
            self._UInt8('ProtectionStatus'),
            _default_=Pass,
            NoProtection=0x00,
            ReadOnly=0x01,
        )

    def _AssociationType(self, **vendor_associations):
        return Enum(
            self._UInt8('ProtectionStatus'),
            _default_=Pass,
            Undefined=0x00,
            GenericFolder=0x01,
            Album=0x02,
            TimeSequence=0x03,
            HorizontalPanoramic=0x04,
            VerticalPanoramic=0x05,
            Panoramic2D=0x06,
            AncillaryData=0x07,
            **vendor_associations
        )

    def _AssociationDesc(self, **vendor_associations):
        return Enum(
            self._UInt8('ProtectionStatus'),
            _default_=Pass,
            Undefined=0x00,
            DefaultPlaybackData=0x03,
            ImagesPerRow=0x06,
            **vendor_associations
        )

    def _ObjectInfo(self):
        '''Return desired endianness for ObjectInfo'''
        return Struct(
            'ObjectInfo',
            self._StorageID,
            Rename('ObjectFormat', self._ObjectFormatCode),
            self._ProtectionStatus,
            self._UInt32('ObjectCompressedSize'),
            Rename('ThumbFormat', self._ObjectFormatCode),
            self._UInt32('ThumbCompressedSize'),
            self._UInt32('ThumbPixWidth'),
            self._UInt32('ThumbPixHeight'),
            self._UInt32('ImagePixWidth'),
            self._UInt32('ImagePixHeight'),
            self._UInt32('ImageBitDepth'),
            Rename('ParentObject', self._ObjectHandle),
            self._AssociationType,
            self._AssociationDesc,
            self._UInt32('SequenceNumber'),
            self._String('Filename'),
            Rename('CaptureDate', self._DateTime),
            Rename('ModificationDate', self._DateTime),
            self._String('Keywords'),
        )

    def _set_endian(self, little=False, big=False):
        '''Instantiate constructors to given endianness'''
        # All constructors need to be instantiated before use by setting their
        # endianness. But only those that don't depend on endian-generic
        # constructors need to be explicitly instantiated to a given
        # endianness.
        self._UInt8 = self._UInt8(_le_=little, _be_=big)
        self._UInt16 = self._UInt16(_le_=little, _be_=big)
        self._UInt32 = self._UInt32(_le_=little, _be_=big)
        self._UInt64 = self._UInt64(_le_=little, _be_=big)
        self._UInt128 = self._UInt128(_le_=little, _be_=big)
        self._Int8 = self._Int8(_le_=little, _be_=big)
        self._Int16 = self._Int16(_le_=little, _be_=big)
        self._Int32 = self._Int32(_le_=little, _be_=big)
        self._Int64 = self._Int64(_le_=little, _be_=big)
        self._Int128 = self._Int128(_le_=little, _be_=big)
        self._Parameter = self._Parameter(_le_=little, _be_=big)

        # Implicit instantiation. Needs to happen after the above.
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

        # TODO: Implement pertinent types and then instantiate.
        self._DataTypeCode = self._DataTypeCode()
        self._DataType = self._DataType()
        self._GetSet = self._GetSet()
        self._FormFlag = self._FormFlag()
        self._DevicePropDesc = self._DevicePropDesc()

    __session = 0
    __session_open = False
    __transaction_id = 0

    @property
    def __transaction(self):
        '''Give magical property for the latest TransactionID'''
        current_id = self.__transaction_id
        self.__transaction_id += 1
        if self.__transaction_id > 0xFFFFFFFE:
            self.__transaction_id = 1
        return current_id

    @__transaction.setter
    def __transaction(self, value):
        '''Manage reset of TransactionID'''
        if value != 0:
            raise PTPError(
                'Current TransactionID should not be set. Only reset.'
            )
        else:
            self.__transaction_id = 0

    def __init__(self):
        raise PTPUnimplemented(
            'Please implement PTP device setup for this transport.'
        )

    def send(self, ptp_container, payload):
        '''Operation with dataphase from initiator to responder'''
        raise PTPUnimplemented(
            'Please implement a PTP dataphase send for this transport.'
        )

    def recv(self, ptp_container):
        '''Operation with dataphase from responder to initiator'''
        raise PTPUnimplemented(
            'Please implement PTP dataphase receive for this transport.'
        )

    def mesg(self, ptp_container):
        '''Operation with no dataphase'''
        raise PTPUnimplemented(
            'Please implement PTP no-dataphase command for this transport.'
        )

    def event(self, wait=False):
        raise PTPUnimplemented(
            'Please implement a PTP event for this transport.'
        )

    @property
    def session_id(self):
        '''Expose internat SessionID'''
        return self.__session

    @session_id.setter
    def session_id(self, value):
        '''Ignore external modifications to SessionID'''
        pass

    @contextmanager
    def session(self):
        '''Manage session with context manager.

        Once transport specifig interfaces are defined, this allows easier,
        more nuclear sessions:

            ptp = PTPUSB()
            with ptp.session():
                ptp.get_device_info()
        '''
        try:
            if not self.__session_open:
                self.open_session()
            yield
        finally:
            if self.__session_open:
                self.close_session()

    def __parse_if_data(self, response, constructor):
        '''If the response contains data, parse it with constructor.'''
        return (constructor.parse(response.Data)
                if hasattr(response, 'Data') else None)

    def open_session(self):
        self.__session += 1
        self.__transaction = 0
        ptp = Container(
            OperationCode='OpenSession',
            # Only the OpenSession operation is allowed to have a 0
            # SessionID, because no session is open yet.
            SessionID=0,
            TransactionID=self.__transaction,
            Parameter=[self.__session]
        )
        response = self.mesg(ptp)
        if response.ResponseCode == 'OK':
            self.__session_open = True
        return response

    def close_session(self):
        ptp = Container(
            OperationCode='CloseSession',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        response = self.mesg(ptp)
        if response.ResponseCode == 'OK':
            self.__session_open = False
        return response

    def reset_device(self):
        ptp = Container(
            OperationCode='ResetDevice',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[],
        )
        response = self.recv(ptp)
        if response.ResponseCode == 'OK':
            self.__session_open = False
        return response

    def power_down(self):
        ptp = Container(
            OperationCode='PowerDown',
            SessionID=self.__session,
            TransactionID=self.__transaction,
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
        if isinstance(device_property, basestring):
            try:
                code = self._PropertyCode.encoding[device_property]
            except Exception:
                raise PTPError('Unknown property name. Try with a number?')
        else:
            code = device_property

        ptp = Container(
            OperationCode='ResetDevice',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[0xffffffff if reset_all else code],
        )
        response = self.recv(ptp)
        return response

    def get_device_info(self):
        ptp = Container(
            OperationCode='GetDeviceInfo',
            SessionID=self.__session,
            # GetrDeviceInfo can happen outside a session. But if there is one
            # running just use that one.
            TransactionID=(self.__transaction if self.__session_open else 0),
            Parameter=[]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._DeviceInfo)

    def get_storage_ids(self):
        ptp = Container(
            OperationCode='GetStorageIDs',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._StorageIDs)

    def get_storage_info(self, storage_id):
        ptp = Container(
            OperationCode='GetStorageInfo',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[storage_id]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._StorageInfo)

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
        # TODO: accept object_format code or its name.
        if object_handle != 0 and in_root and object_handle != 0xffffffff:
            raise ValueError(
                'Cannot get both root and {}'.format(object_handle)
            )
        ptp = Container(
            OperationCode='GetNumObjects',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[
                0xffffffff if all_storage_ids else storage_id,
                0xffffffff if all_formats else object_format,
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
        ptp = Container(
            OperationCode='GetObjectHandles',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[
                0xffffffff if all_storage_ids else storage_id,
                0xffffffff if all_formats else object_format,
                0xffffffff if in_root else object_handle
            ]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(
            response,
            self._PTPArray('ObjectHandles', self._ObjectHandle)
        )

    def get_device_prop_desc(self, device_property):
        '''Retrieve the property description.

        Accepts a property name of a number.
        '''
        # TODO: Define DevicePropDesc constructor.
        if isinstance(device_property, basestring):
            try:
                code = self._PropertyCode.encoding[device_property]
            except Exception:
                raise PTPError('Unknown property name. Try with a number?')
        else:
            code = device_property
        ptp = Container(
            OperationCode='GetDevicePropDesc',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[code]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._DevicePropDesc)

    def get_device_prop_value(self, device_property):
        # TODO: Define DevicePropValue constructor.
        if isinstance(device_property, basestring):
            try:
                code = self._PropertyCode.encoding[device_property]
            except Exception:
                raise PTPError('Unknown property name. Try with a number?')
        else:
            code = device_property

        ptp = Container(
            OperationCode='GetDevicePropValue',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[code],
        )
        response = self.recv(ptp)
        return response
        # return self.__parse_if_data(response, self._DevicePropValue)

    def initiate_capture(self, storage_id=0, object_format=0):
        # TODO: accept format codes or names
        ptp = Container(
            OperationCode='InitiateCapture',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[
                storage_id,
                object_format,
            ]
        )
        response = self.recv(ptp)
        return response

    def initiate_open_capture(self, storage_id=0, object_format=0):
        '''Initiate open capture in `storage_id` of type `object_format`.'''
        # TODO: accept format codes or names
        ptp = Container(
            OperationCode='InitiateOpenCapture',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[
                storage_id,
                object_format,
            ]
        )
        response = self.recv(ptp)
        return response

    def terminate_open_capture(self, transaction_id):
        '''Terminate the open capture initiated in `transaction_id`'''
        ptp = Container(
            OperationCode='TerminateOpenCapture',
            SessionID=self.__session,
            TransactionID=self.__transaction,
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
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[handle]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._ObjectInfo)

    def send_object(self, bytes_data):
        '''Send object to responder.

        The object should correspond to the latest SendObjectInfo interaction
        between Initiator and Responder.
        '''
        ptp = Container(
            OperationCode='SendObject',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        response = self.send(ptp, bytes_data)
        if response.ResponseCode != 'OK':
            response = self.send(ptp, bytes_data)
        return response
