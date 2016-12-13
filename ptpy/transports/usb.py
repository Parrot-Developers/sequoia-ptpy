'''This module implements the USB transport layer for PTP.

It exports the PTPUSB class. Both the transport layer and the basic PTP
implementation are Vendor agnostic. Vendor extensions should extend these to
support more operations.
'''
from __future__ import absolute_import
import usb.core
import six
from usb.util import (
    endpoint_type, endpoint_direction, ENDPOINT_TYPE_BULK, ENDPOINT_TYPE_INTR,
    ENDPOINT_OUT, ENDPOINT_IN,
)
from ..ptp import PTPError
from construct import (
    Array, Bytes, Container, Embedded, Enum, ExprAdapter, Range, Struct,
    Int16ul, Int32ul, Pass
)
from threading import Thread, Event
from threading import enumerate as threading_enumerate
from six.moves.queue import Queue
import atexit


__all__ = ('USBTransport', 'find_usb_cameras')
__author__ = 'Luis Mario Domenzain'

PTP_USB_CLASS = 6


def _main_thread_alive():
    return any(
        (i.name == "MainThread") and i.is_alive() for i in
        threading_enumerate())


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


class USBTransport(object):
    '''Implement USB transport.'''
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
                usb.util.claim_interface(self.__dev, self.__intf)
            except usb.core.USBError:
                raise PTPError(
                        'Could not detach kernel driver.\n'
                        'Maybe the camera is mounted?'
                        )
        usb.util.claim_interface(self.__dev, self.__intf)
        self.__event_queue = Queue()
        self.__event_shutdown = Event()
        self.__event_proc = Thread(target=self.__poll_events)
        self.__event_proc.daemon = False
        atexit.register(self._shutdown)
        self.__event_proc.start()

    def _shutdown(self):
        self.__event_shutdown.set()
        # Free USB resource on shutdown.

        # Only join a running thread.
        if self.__event_proc.is_alive():
            self.__event_proc.join(2)

        usb.util.release_interface(self.__dev, self.__intf)

    # Helper methods.
    # ---------------------
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
        self._set_endian('little')

        self.__Length = Int32ul
        self.__Type = Enum(
                Int16ul,
                default=Pass,
                Undefined=0x0000,
                Command=0x0001,
                Data=0x0002,
                Response=0x0003,
                Event=0x0004,
                )
        # This is just a convenience constructor to get the size of a header.
        self.__Code = Int16ul
        self.__Header = Struct(
                'Length' / self.__Length,
                'Type' / self.__Type,
                'Code' / self.__Code,
                'TransactionID' / self._TransactionID,
                )
        # These are the actual constructors for parsing and building.
        self.__CommandHeader = Struct(
                'Length' / self.__Length,
                'Type' / self.__Type,
                'OperationCode' / self._OperationCode,
                'TransactionID' / self._TransactionID,
                )
        self.__ResponseHeader = Struct(
                'Length' / self.__Length,
                'Type' / self.__Type,
                'ResponseCode' / self._ResponseCode,
                'TransactionID' / self._TransactionID,
                )
        self.__EventHeader = Struct(
                'Length' / self.__Length,
                'Type' / self.__Type,
                'EventCode' / self._EventCode,
                'TransactionID' / self._TransactionID,
                )
        # Apparently nobody uses the SessionID field. Even though it is
        # specified in ISO15740:2013(E), no device respects it and the session
        # number is implicit over USB.
        self.__Param = Range(0, 5, self._Parameter)
        self.__FullParam = Struct(Array(5, self._Parameter))
        self.__FullEventParam = Struct(Array(3, self._Parameter))
        self.__CommandTransactionBase = Struct(
                Embedded(self.__CommandHeader),
                'Payload' / Bytes(
                    lambda ctx, h=self.__Header: ctx.Length - h.sizeof()
                )
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
                Embedded(self.__ResponseHeader),
                'Payload' / Bytes(
                    lambda ctx, h=self.__Header: ctx.Length - h.sizeof())
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
                Embedded(self.__EventHeader),
                'Payload' / Bytes(
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

    def __parse_response(self, usbdata):
        '''Helper method for parsing USB data.'''
        # Build up container with all PTP info.
        usbdata = bytearray(usbdata)
        transaction = self.__ResponseTransaction.parse(usbdata)
        response = Container(
            SessionID=self.session_id,
            TransactionID=transaction.TransactionID,
        )
        if transaction.Type == 'Response':
            response['ResponseCode'] = transaction.ResponseCode
            response['Parameter'] = self.__Param.parse(transaction.Payload)
        elif transaction.Type == 'Event':
            event = self.__EventHeader.parse(
                usbdata[0:self.__Header.sizeof()]
            )
            response['EventCode'] = event.EventCode
            response['Parameter'] = self.__Param.parse(transaction.Payload)
        else:
            command = self.__CommandHeader.parse(
                usbdata[0:self.__Header.sizeof()]
            )
            response['OperationCode'] = command.OperationCode
            response['Data'] = transaction.Payload
        return response

    def __recv(self, event=False, wait=False, raw=False):
        '''Helper method for receiving non-event data.'''
        # TODO: clear stalls automatically
        ep = self.__intep if event else self.__inep
        try:
            usbdata = ep.read(ep.wMaxPacketSize, timeout=0 if wait else 5)
        except usb.core.USBError as e:
            # Ignore timeout or busy device once.
            if e.errno == 110 or e.errno == 16:
                if event:
                    return None
                else:
                    usbdata = ep.read(
                        ep.wMaxPacketSize,
                        timeout=5000
                    )
            else:
                raise e
        header = self.__ResponseHeader.parse(
            bytearray(usbdata[0:self.__Header.sizeof()])
        )
        if header.Type not in ['Response', 'Data', 'Event']:
            raise PTPError(
                'Unexpected USB transfer type.'
                'Expected Response, Event or Data but reveived {}'
                .format(header.Type)
            )
        while len(usbdata) < header.Length:
            usbdata += ep.read(
                ep.wMaxPacketSize,
                timeout=5000
            )
        if raw:
            return usbdata
        else:
            return self.__parse_response(usbdata)

    def __send(self, ptp_container, event=False):
        '''Helper method for sending data.'''
        ep = self.__intep if event else self.__outep
        transaction = self.__CommandTransaction.build(ptp_container)
        try:
            ep.write(transaction, timeout=1)
        except usb.core.USBError as e:
            # Ignore timeout or busy device once.
            if e.errno == 110 or e.errno == 16:
                ep.write(transaction, timeout=5000)

    def __send_request(self, ptp_container):
        '''Send PTP request without checking answer.'''
        # Don't modify original container to keep abstraction barrier.
        ptp = Container(**ptp_container)
        # Don't send unused parameters
        try:
            while not ptp.Parameter[-1]:
                ptp.Parameter.pop()
                if len(ptp.Parameter) == 0:
                    break
        except IndexError:
            # The Parameter list is already empty.
            pass

        # Send request
        ptp['Type'] = 'Command'
        ptp['Payload'] = self.__Param.build(ptp.Parameter)
        self.__send(ptp)

    def __send_data(self, ptp_container, data):
        '''Send data without checking answer.'''
        # Don't modify original container to keep abstraction barrier.
        ptp = Container(**ptp_container)
        # Send data
        ptp['Type'] = 'Data'
        ptp['Payload'] = data
        self.__send(ptp)

    # Actual implementation
    # ---------------------
    def send(self, ptp_container, data):
        '''Transfer operation with dataphase from initiator to responder'''
        self.__send_request(ptp_container)
        self.__send_data(ptp_container, data)
        # Get response and sneak in implicit SessionID and missing parameters.
        return self.__recv()

    def recv(self, ptp_container):
        '''Transfer operation with dataphase from responder to initiator.'''
        self.__send_request(ptp_container)
        dataphase = self.__recv()
        if hasattr(dataphase, 'Data'):
            response = self.__recv()
            if (
                    (ptp_container.OperationCode != dataphase.OperationCode) or
                    (ptp_container.TransactionID != dataphase.TransactionID) or
                    (ptp_container.SessionID != dataphase.SessionID) or
                    (dataphase.TransactionID != response.TransactionID) or
                    (dataphase.SessionID != response.SessionID)
            ):
                raise PTPError(
                    'Dataphase does not match with requested operation.'
                )
            response['Data'] = dataphase.Data
            return response
        else:
            return dataphase

    def mesg(self, ptp_container):
        '''Transfer operation without dataphase.'''
        self.__send_request(ptp_container)
        # Get response and sneak in implicit SessionID and missing parameters
        # for FullResponse.
        return self.__recv()

    def event(self, wait=False):
        '''Check event.

        If `wait` this function is blocking. Otherwise it may return None.
        '''
        evt = None
        usbdata = None
        timeout = None if wait else 0.001
        if not self.__event_queue.empty():
            usbdata = self.__event_queue.get(block=not wait, timeout=timeout)
        if usbdata is not None:
            evt = self.__parse_response(usbdata)

        return evt

    def __poll_events(self):
        '''Poll events, adding them to a queue.'''
        while not self.__event_shutdown.is_set() and _main_thread_alive():
            evt = self.__recv(event=True, wait=False, raw=True)
            if evt is not None:
                self.__event_queue.put(evt)
