'''This module implements the USB transport layer for PTP'''
import usb.core
import usb.util
import ptp.py

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

# Find all devices that say they're still cameras (class 6)
devs = usb.core.find(find_all=True, custom_match=find_class(6))

for dev in devs:
    # Attempt to use the first configuration with the first interface
    print dev
