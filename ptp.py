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
        Container, Struct, Enum, UNInt16, UNInt32, Array, BitField, ULInt16,
        ULInt32, UBInt16, UBInt32
        )
from contextlib import contextmanager

__all__ = (
        'PTPError', 'PTPUnimplemented', 'SessionID', 'TransactionID',
        'OperationCode', 'ResponseCode', 'EventCode', 'Event', 'Response',
        'Operation', 'PTPDevice',
        )

__author__ = 'Luis Mario Domenzain'


# Exceptions
class PTPError(Exception):
    '''PTP implementation exceptions.'''
    pass


class PTPUnimplemented(PTPError):
    '''Exception to indicate missing implementation.'''
    pass


def switch_endian(le, be, l, b, n):
    '''Return little, native or big endian.'''
    if (be != le):
        return l if le else b
    elif le:
        raise PTPError('Cannot be both little and big endian...')
    else:
        return n


# Apparently nobody uses the SessionID field. Even though it is specified in
# ISO15740:2013(E), no device respects it and the session number is implicit.
def SessionID(le=False, be=False):
    '''Return desired endianness for SessionID'''
    subcon = switch_endian(le, be, ULInt32, UBInt32, UNInt32)
    return subcon('SessionID')


def TransactionID(le=False, be=False):
    '''Return desired endianness for TransactionID'''
    subcon = switch_endian(le, be, ULInt32, UBInt32, UNInt32)
    return subcon('TransactionID')

Parameter = BitField('Parameter', 32)


def OperationCode(le=False, be=False):
    '''Return desired endianness for known OperationCode'''
    subcon = switch_endian(le, be, ULInt16, UBInt16, UNInt16)
    return Enum(
        subcon('OperationCode'),
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
        _default_='UnknownOperation',
        )


def ResponseCode(le=False, be=False):
    '''Return desired endianness for known ResponseCode'''
    subcon = switch_endian(le, be, ULInt16, UBInt16, UNInt16)
    return Enum(
        subcon('ResponseCode'),
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
        _default_='UnknownResponse',
        )


def EventCode(le=False, be=False):
    '''Return desired endianness for known EventCode'''
    subcon = switch_endian(le, be, ULInt16, UBInt16, UNInt16)
    return Enum(
        subcon('EventCode'),
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
        _default_='UnknownEvent',
        )
Event = Struct(
        'Event',
        EventCode(),
        SessionID(),
        TransactionID(),
        Array(3, Parameter),
        )
Response = Struct(
        'Response',
        ResponseCode(),
        SessionID(),
        TransactionID(),
        Array(5, Parameter),
        )
Operation = Struct(
        'Operation',
        OperationCode(),
        SessionID(),
        TransactionID(),
        Array(5, Parameter),
        )


class PTPDevice(object):
    '''Implement bare PTP Device. Vendor specifics should extend it.'''
    # These constructors are provided as a tentative interface. Each transport
    # layer may use them as they are or modify them. For instance, over most
    # USB cameras session is implicit and should be left out.
    __Operation = Operation
    __Response = Response
    __Event = Event

    __session = 0
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
            self.open_session()
            yield
        finally:
            self.close_session()

    def open_session(self):
        self.__session += 1
        self.__transaction = 0
        ptp = Container(
            OperationCode='OpenSession',
            # Only the OpenSession operation is allowed to have a 0
            # SessionID, because no session is open yet.
            SessionID=0,
            TransactionID=self.__transaction,
            Parameter=[self.__session, 0, 0, 0, 0]
            )
        response = self.mesg(ptp)
        return response

    def close_session(self):
        ptp = Container(
            OperationCode='CloseSession',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[0, 0, 0, 0, 0]
            )
        response = self.mesg(ptp)
        return response
