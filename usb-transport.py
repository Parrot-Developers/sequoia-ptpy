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
from ptp import PTPError
from parrot import PTPDevice
from construct import (
        Container, Array, ULInt32, ULInt16, Struct, Bytes, ExprAdapter,
        Embedded, Enum, Range, Debugger
        )

__all__ = ('PTPUSB', 'find_usb_cameras')
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


def find_usb_cameras():
        return usb.core.find(
            find_all=True,
            custom_match=find_class(PTP_USB_CLASS)
        )


class PTPUSB(PTPDevice):
    '''Implement bare PTP Device with USB transport.'''

    def __init__(self, dev=None):
        '''Instantiate the first available PTP device over USB'''
        self.__setup_constructors()
        # If no device is specified, find all devices claiming to be Cameras
        # and get the USB endpoints for the first one that works.
        cameras = find_usb_cameras()
        devs = [dev] if (dev is not None) else cameras

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

    def __setup_constructors(self):
        '''Set endianness and create transport-specific constructors.'''
        # Set endianness of constructors before using them.
        self._set_endian(little=True)

        self.__Length = ULInt32('Length')
        self.__Type = Enum(
                ULInt16('Type'),
                Undefined=0x0000,
                Command=0x0001,
                Data=0x0002,
                Response=0x0003,
                Event=0x0004,
                )
        # This is just a convenience constructor to get the size of a header.
        self.__Code = ULInt16('Code')
        self.__Header = Struct(
                'Header',
                self.__Length,
                self.__Type,
                self.__Code,
                self._TransactionID,
                )
        # These are the actual constructors for parsing and building.
        self.__CommandHeader = Struct(
                'CommandHeader',
                self.__Length,
                self.__Type,
                self._OperationCode,
                self._TransactionID,
                )
        self.__ResponseHeader = Struct(
                'ResponseHeader',
                self.__Length,
                self.__Type,
                self._ResponseCode,
                self._TransactionID,
                )
        self.__EventHeader = Struct(
                'EventHeader',
                self.__Length,
                self.__Type,
                self._EventCode,
                self._TransactionID,
                )
        # Apparently nobody uses the SessionID field. Even though it is
        # specified in ISO15740:2013(E), no device respects it and the session
        # number is implicit over USB.
        self.__Param = Struct('Parameter', Range(0, 5, self._Parameter))
        self.__FullParam = Struct('Parameter', Array(5, self._Parameter))
        self.__FullEventParam = Struct('Parameter', Array(3, self._Parameter))
        self.__CommandTransactionBase = Struct(
                'Command',
                Embedded(self.__CommandHeader),
                Bytes('Payload',
                      lambda ctx, h=self.__Header: ctx.Length - h.sizeof()),
                )
        self.__CommandTransaction = ExprAdapter(
                self.__CommandTransactionBase,
                encoder=lambda obj, ctx, h=self.__Header: Container(
                    Length=len(obj.Payload) + h.sizeof(),
                    **obj
                    ),
                decoder=lambda obj, ctx: obj,
                )
        self.__ResponseTransactionBase = Struct(
                'Response',
                Embedded(self.__ResponseHeader),
                Bytes('Payload',
                      lambda ctx, h=self.__Header: ctx.Length - h.sizeof()),
                )
        self.__ResponseTransaction = ExprAdapter(
                self.__ResponseTransactionBase,
                encoder=lambda obj, ctx, h=self.__Header: Container(
                    Length=len(obj.Payload) + h.sizeof(),
                    **obj
                    ),
                decoder=lambda obj, ctx: obj,
                )
        self.__EventTransactionBase = Struct(
                'Event',
                Embedded(self.__EventHeader),
                Bytes('Payload',
                      lambda ctx, h=self.__Header: ctx.Length - h.sizeof()),
                )
        self.__EventTransaction = ExprAdapter(
                self.__EventTransactionBase,
                encoder=lambda obj, ctx, h=self.__Header: Container(
                    Length=len(obj.Payload) + h.sizeof(),
                    **obj
                    ),
                decoder=lambda obj, ctx: obj,
                )

    def __recv(self):
        '''Helper method for receiving non-event data.'''
        # Read up two megabytes and let PyUSB manage the looping.
        try:
            transaction = self.__inep.read(2*(10**6), timeout=1)
        except usb.core.USBError as e:
            # Ignore timeout once.
            if e.errno == 110:
                transaction = self.__inep.read(2*(10**6), timeout=5000)
            else:
                raise e
        header = self.__ResponseHeader.parse(
            transaction[0:self.__Header.sizeof()]
        )
        if header.Type not in ['Response', 'Data']:
            raise PTPError(
                'Unexpected USB transfer type.'
                'Expected Response or Data but reveived {}'.format(
                    transaction.Type
                )
            )
        while len(transaction) < header.Length:
            transaction += self.__inep.read(2*(10**6))
        return self.__ResponseTransaction.parse(transaction)

    def __send(self, ptp_container):
        '''Helper method for sending data.'''
        transaction = self.__CommandTransaction.build(ptp_container)
        self.__outep.write(transaction)

    def send(self, ptp_container, data):
        '''Transfer operation with dataphase from initiator to responder'''
        # Don't modify original container to keep abstraction barrier.
        ptp = Container(**ptp_container)
        # Don't send unused parameters
        while not ptp.Parameter[-1]:
            ptp.Parameter.pop()
            if len(ptp.Parameter) == 0:
                break
        # Send request
        ptp['Type'] = 'Command'
        ptp['Payload'] = self.__Param.build(ptp)
        self.__send(ptp)
        # Send data
        ptp['Type'] = 'Data'
        ptp['Payload'] = data
        self.__send(ptp)
        # Get response and sneak in implicit SessionID and missing parameters.
        transaction = self.__recv()
        payload = transaction.Payload
        response = self.__Param.parse(payload)
        response['SessionID'] = self.session_id
        response.Parameter = (
                response.Parameter +
                (5 - len(response.Parameter))*[0]
                )
        return response

    def recv(self, ptp_container):
        '''Transfer operation with dataphase from responder to initiator.'''
        # Don't modify original container to keep abstraction barrier.
        ptp = Container(**ptp_container)
        # Don't send unused parameters
        while not ptp.Parameter[-1]:
            ptp.Parameter.pop()
            if len(ptp.Parameter) == 0:
                break
        # Send request
        ptp['Type'] = 'Command'
        ptp['Payload'] = Debugger(self.__Param).build(ptp)
        self.__send(ptp)
        # Read data
        dataphase = self.__recv()
        if dataphase.Type == 'Response':
            payload = dataphase.Payload
            response = self.__Param.parse(payload)
            response['SessionID'] = self.session_id
            response.Parameter = (
                    response.Parameter +
                    (5 - len(response.Parameter))*[0]
                    )
            return response
        # Get response and sneak in implicit SessionID, Data and missing
        # parameters.
        transaction = self.__recv()
        # TODO: refactor this to appear only in one place.
        payload = transaction.Payload
        response = self.__Param.parse(payload)
        response['SessionID'] = self.session_id
        response['Data'] = dataphase.Payload
        response.Parameter = (
                response.Parameter +
                (5 - len(response.Parameter))*[0]
                )
        return response

    def mesg(self, ptp_container):
        '''Transfer operation without dataphase.'''
        # Don't modify original container to keep abstraction barrier.
        ptp = Container(**ptp_container)
        # Don't send unused parameters
        while not ptp.Parameter[-1]:
            ptp.Parameter.pop()
            if len(ptp.Parameter) == 0:
                break
        # Send request
        ptp['Type'] = 'Command'
        ptp['Payload'] = self.__Param.build(ptp)
        self.__send(ptp)
        # Get response and sneak in implicit SessionID and missing parameters
        # for FullResponse.
        transaction = self.__recv()
        payload = transaction.Payload
        response = self.__Param.parse(payload)
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
                    self.__FullEventParam.sizeof() +
                    self.__EventHeader.sizeof(),
                    timeout=0 if wait else 1
                    )
        except usb.core.USBError as e:
            # Ignore timeout.
            if e.errno == 110:
                return None
        # Check for event adding SessionID, and parameters as necessary.
        transaction = self.__EventTransaction.parse(response)
        if transaction.Type != 'Event':
            raise PTPError(
                'Unexpected USB transfer type.'
                'Expected Event but reveived {}'.format(transaction.Type)
            )
        payload = transaction.Payload
        event = self.__Param.parse(payload)
        event.Parameter = event.Parameter + (3 - len(event.Parameter))*[0]
        event['SessionID'] = self.session_id
        event['TransactionID'] = transaction.TransactionID
        event['EventCode'] = transaction.EventCode
        return event


if __name__ == "__main__":
    devs = find_usb_cameras()
    for dev in devs:
        camera = PTPUSB(dev)
        print camera.get_device_info()
        with camera.session():
            ids = camera.get_storage_ids()
            print ids
            for storage in ids:
                print camera.get_storage_info(storage)
            print camera.event(wait=True)
            print camera.get_device_prop_desc(0x5002)
