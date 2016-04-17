'''This module implements the USB transport layer for PTP'''
import usb.core
from usb.util import (
        endpoint_type, endpoint_direction, ENDPOINT_TYPE_BULK,
        ENDPOINT_TYPE_INTR, ENDPOINT_OUT, ENDPOINT_IN
        )
from ptp import (  # noqa
        PTPDevice, PTPError, ResponseCode, EventCode, OperationCode,
        TransactionID, Parameter
        )

from construct import (  # noqa
        Container, Array, ULInt32, ULInt16, ULInt8, Struct, Bytes,
        ExprAdapter
        )


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
    __Type = ULInt16('Type')
    __Operation = Struct(
            'Operation',
            OperationCode(le=True),
            TransactionID(le=True),
            Array(5, Parameter),
            )
    __Response = Struct(
            'Response',
            ResponseCode(le=True),
            TransactionID(le=True),
            Array(5, Parameter),
            )
    __Event = Struct(
            'Event',
            __Length,
            __Type,
            OperationCode(le=True),
            TransactionID(le=True),
            Array(3, Parameter)
            )
    __Transaction = ExprAdapter(
            Struct(
                'Transaction',
                __Length,
                __Type,
                Bytes('Payload', lambda ctx: ctx.__Length),
                ),
            encoder=lambda obj, ctx: Container(Length=len(obj), **obj),
            decoder=lambda obj, ctx: Container(
                **{obj[field] for field in obj if field != 'Length'}
                ),
            )

    def __init__(self, dev=None):
        '''Instantiate the first available PTP device over USB'''
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

    def send(self, ptp_container, payload):
        pass

    def recv(self, ptp_container):
        pass

    def mesg(self, ptp_container):
        self.__outep.write(self.__Operation.build(ptp_container))
        response = self.__inep.read(self.__Response.sizeof())
        return response

    def event(self, wait=False):
        response = None
        try:
            response = self.__intep.read(
                    self.__Event.sizeof(),
                    timeout=0 if wait else 1
                    )
        except usb.core.USBError as e:
            # Ignore timeout.
            if e.errno == 110:
                pass

        return response

if __name__ == "__main__":
    camera = PTPUSB()
    print camera.open_session()
    print camera.close_session()
    print camera.event()
