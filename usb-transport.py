'''This module implements the USB transport layer for PTP.

It exports the PTPUSB class. Both the transport layer and the basic PTP
impelementation are Vendor agnostic. Vendor extensions should extend these to
support more operations.
'''
import usb.core
from usb.util import (
        endpoint_type, endpoint_direction, ENDPOINT_TYPE_BULK,
        ENDPOINT_TYPE_INTR, ENDPOINT_OUT, ENDPOINT_IN
        )
from ptp import (
        PTPDevice, PTPError, ResponseCode, EventCode, OperationCode,
        TransactionID, Parameter
        )
from construct import (
        Container, Array, ULInt32, ULInt16, Struct, Bytes, ExprAdapter,
        Embedded, Enum, Range
        )

__all__ = ('PTPUSB',)
__author__ = 'Luis Mario Domenzain'

PTP_USB_CLASS = 6


class find_class(object):
    def __init__(self, class_):
        self._class = class_

    def __call__(self, device):
        if device.bDeviceClass == self._class:
            return True
        for cfg in device:
            intf = usb.util.find_descriptor(
                cfg,
                bInterfaceClass=self._class
            )
            if intf is not None:
                return True
        return False


class PTPUSB(PTPDevice):
    '''Implement bare PTP Device with USB transport.'''
    # Redefine constructors for USB.
    __Length = ULInt32('Length')
    __Type = Enum(
            ULInt16('Type'),
            Undefined=0x0000,
            Command=0x0001,
            Data=0x0002,
            Response=0x0003,
            Event=0x0004,
            )
    __Header = Struct(
            'Header',
            __Length,
            __Type,
            )
    __Operation = Struct(
            'Operation',
            OperationCode(_le_=True),
            TransactionID(_le_=True),
            Array(5, Parameter),
            )
    __FullResponse = Struct(
            'Response',
            ResponseCode(_le_=True),
            TransactionID(_le_=True),
            Array(5, Parameter),
            )
    __PartialResponse = Struct(
            'Response',
            ResponseCode(_le_=True),
            TransactionID(_le_=True),
            Range(0, 5, Parameter),
            )
    __FullEvent = Struct(
            'Event',
            EventCode(_le_=True),
            TransactionID(_le_=True),
            Array(3, Parameter)
            )
    __PartialEvent = Struct(
            'Event',
            EventCode(_le_=True),
            TransactionID(_le_=True),
            Range(0, 3, Parameter)
            )
    __TransactionBase = Struct(
            'Transaction',
            Embedded(__Header),
            Bytes('Payload', lambda ctx, h=__Header: ctx.Length - h.sizeof()),
            )
    __Transaction = ExprAdapter(
            __TransactionBase,
            encoder=lambda obj, ctx, h=__Header: Container(
                Length=len(obj.Payload) + h.sizeof(),
                **obj
                ),
            decoder=lambda obj, ctx: obj,
            )

    def __init__(self, dev=None):
        '''Instantiate the first available PTP device over USB'''
        self._set_endian(little=True)
        # Find all devices claiming to be Cameras and get the endpoints for the
        # first one that works.
        devs = usb.core.find(
                find_all=True,
                custom_match=find_class(PTP_USB_CLASS)
                )
        if dev is not None:
            devs = [dev]

        for dev in devs:
            if self.__setup_device(dev):
                break
        else:
            raise PTPError('No USB PTP device found.')

        if self.__dev.is_kernel_driver_active(self.__intf.bInterfaceNumber):
            try:
                self.__dev.detach_kernel_driver(self.__intf.bInterfaceNumber)
            except usb.core.USBError:
                raise PTPError(
                        'Could not detach kernel driver.\n'
                        'Maybe the camera is mounted?'
                        )
                usb.util.claim_interface(self.__dev, self.__intf)

    def __setup_device(self, dev):
        '''Get endpoints for a device. True on success.'''
        self.__inep = None
        self.__outep = None
        self.__intep = None
        self.__cfg = None
        self.__dev = None
        self.__intf = None
        # Attempt to find the USB in, out and interrupt endpoints for a PTP
        # interface.
        for cfg in dev:
            for intf in cfg:
                if intf.bInterfaceClass == PTP_USB_CLASS:
                    for ep in intf:
                        ep_type = endpoint_type(ep.bmAttributes)
                        ep_dir = endpoint_direction(ep.bEndpointAddress)
                        if ep_type == ENDPOINT_TYPE_BULK:
                            if ep_dir == ENDPOINT_IN:
                                self.__inep = ep
                            elif ep_dir == ENDPOINT_OUT:
                                self.__outep = ep
                        elif ((ep_type == ENDPOINT_TYPE_INTR) and
                                (ep_dir == ENDPOINT_IN)):
                            self.__intep = ep
                if not (self.__inep and self.__outep and self.__intep):
                    self.__inep = None
                    self.__outep = None
                    self.__intep = None
                else:
                    self.__cfg = cfg
                    self.__dev = dev
                    self.__intf = intf
                    return True
        return False

    def __recv(self):
        '''Helper method for receiving non-event data.'''
        # Read a full response in one go, and in two goes if there is data.
        transaction = self.__inep.read(
                self.__FullResponse.sizeof() +
                self.__Header.sizeof()
                )
        header = self.__Header.parse(transaction[0:self.__Header.sizeof()])
        if header.Type != 'Response' and header.Type != 'Data':
            raise PTPError('Unexpected USB')
        remaining = header.Length - len(transaction)
        if remaining > 0:
            transaction += self.__inep.read(remaining)
        return self.__Transaction.parse(transaction)

    def __send(self, ptp_container):
        '''Helper method for sending data.'''
        transaction = self.__Transaction.build(ptp_container)
        self.__outep.write(transaction)

    def send(self, ptp_container, data):
        '''Transfer operation with dataphase from initiator to responder'''

    def recv(self, ptp_container):
        '''Transfer operation with dataphase from responder to initiator.'''

    def mesg(self, ptp_container):
        '''Transfer operation without dataphase.'''
        # Don't modify original container to keep abstraction barrier.
        ptp = Container(**ptp_container)

        operation = self.__Operation.build(ptp)
        ptp['Type'] = 'Command'
        ptp['Payload'] = operation
        self.__send(ptp)
        # Get actual response and sneak in implicit SessionID and mising
        # parameters for FullResponse.
        transaction = self.__recv()
        payload = transaction.Payload
        response = self.__PartialResponse.parse(payload)
        response['SessionID'] = self.session_id
        response.Parameter = (
                response.Parameter +
                (5 - len(response.Parameter))*[0]
                )
        return response

    def event(self, wait=False):
        '''Check event.

        If `wait` this function is blocking. Otherwise it may return None.
        '''
        try:
            response = self.__intep.read(
                    self.__FullEvent.sizeof() +
                    self.__Header.sizeof(),
                    timeout=0 if wait else 1
                    )
        except usb.core.USBError as e:
            # Ignore timeout.
            if e.errno == 110:
                return None
        transaction = self.__Transaction.parse(response)
        payload = transaction.Payload
        event = self.__PartialEvent.parse(payload)
        event.Parameter = event.Parameter + (3 - len(event.Parameter))*[0]
        event['SessionID'] = self.session_id
        return event

if __name__ == "__main__":
    camera = PTPUSB()
    print 'Open and close.'
    print camera.open_session()
    print camera.close_session()

    print 'Event wait with context manager.'
    with camera.session():
        for i in range(10):
            print camera.event(wait=True)
