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
    Container, Array, ULInt32, ULInt16, Struct, Bytes, ExprAdapter, Embedded,
    Enum, Range
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
        self.__Param = Range(0, 5, self._Parameter)
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
        try:
            usbdata = self.__inep.read(2*(10**6), timeout=1)
        except usb.core.USBError as e:
            # Ignore timeout once.
            if e.errno == 110:
                usbdata = self.__inep.read(2*(10**6), timeout=5000)
            else:
                raise e
        header = self.__ResponseHeader.parse(usbdata[0:self.__Header.sizeof()])
        command = self.__CommandHeader.parse(usbdata[0:self.__Header.sizeof()])
        if header.Type not in ['Response', 'Data']:
            raise PTPError(
                'Unexpected USB transfer type.'
                'Expected Response or Data but reveived {}'.format(header.Type)
            )
        while len(usbdata) < header.Length:
            # TODO: fix case when data is larger than max USB packet size
            usbdata += self.__inep.read(2*(10**6))

        # Build up container with all PTP info.
        transaction = self.__ResponseTransaction.parse(usbdata)
        response = Container(
            SessionID=self.session_id,
            TransactionID=transaction.TransactionID,
        )
        if transaction.Type == 'Response':
            response['ResponseCode'] = transaction.ResponseCode
            response['Parameter'] = self.__Param.parse(transaction.Payload)
        else:
            response['OperationCode'] = command.OperationCode
            response['Data'] = transaction.Payload
        return response

    def __send(self, ptp_container):
        '''Helper method for sending data.'''
        transaction = self.__CommandTransaction.build(ptp_container)
        try:
            self.__outep.write(transaction, timeout=1)
        except usb.core.USBError as e:
            # Ignore timeout once
            if e.errno == 110:
                self.__outep.write(transaction, timeout=5000)

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
        # Check for event adding SessionID.
        transaction = self.__EventTransaction.parse(response)
        if transaction.Type != 'Event':
            raise PTPError(
                'Unexpected USB transfer type.'
                'Expected Event but reveived {}'.format(transaction.Type)
            )
        payload = transaction.Payload
        event = Container()
        event['Parameter'] = self.__Param.parse(payload)
        event['SessionID'] = self.session_id
        event['TransactionID'] = transaction.TransactionID
        event['EventCode'] = transaction.EventCode
        return event


if __name__ == "__main__":
    devs = find_usb_cameras()
    for dev in devs:
        camera = PTPUSB(dev)
        device_info = camera.get_device_info()
        with camera.session():
            device_info = camera.get_device_info()

            for prop in device_info.DevicePropertiesSupported:
                print camera.get_device_prop_desc(prop)

            handles = camera.get_object_handles(
                None,
                all_formats=True,
                all_storage_ids=True
            )

            for handle in handles:
                print camera.get_object_info(handle)
