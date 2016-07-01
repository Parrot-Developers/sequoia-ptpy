'''Master module that instantiates the correct extension and transport.'''
from __future__ import absolute_import
from .extensions.canon import PTPDevice as canon
from .extensions.microsoft import PTPDevice as mtp
from .extensions.parrot import PTPDevice as parrot
from .ptp import PTPDevice, PTPError
from .transports.usb import USBTransport as usb


class PTPyError(Exception):
    pass

# As extensions are implemented, they should be added here, so they are
# automatically used. The names here need to match those in ptp.py
# VendorExtensionID.
known_extensions = {
    'EastmanKodak': None,
    'SeikoEpson': None,
    'Agilent': None,
    'Polaroid': None,
    'AgfaGevaert': None,
    'Microsoft': mtp,
    'Equinox': None,
    'Viewquest': None,
    'STMicroelectronics': None,
    'Nikon': None,
    'Canon': canon,
    'FotoNation': None,
    'PENTAX': None,
    'Fuji': None,
    'Sony': None,
    'Samsung': None,
    'Parrot': parrot,
}


class PTPyMeta(type):
    '''
    Metaclass for automatically identifiyng and loading PTP extensions in PTPy.
    '''
    def __new__(cls, device=None, extension=None, transport=None, autobuild=True):
        plain = ptpy_factory(transport)
        try:
            plain_camera = plain()
        except PTPError:
            plain_camera = None

        if device is not None:
            device_info = device.get_device_info()
            device._shutdown()
            try:
                extension = known_extensions[device_info.VendorExtensionID]
            except KeyError:
                extension = None

            PTPy = ptpy_factory(
                transport,
                extension
            )

    # TODO: Add a raw option to get a pure PTP device, and default to a smart
    # device that manages properties automatically.

class PTPy(metaclass=PTPyMeta):
    def __init__(self, extension=None, transport=None, knowledge=True):
        # Query the device for information on all its properties and update
        # when there are changes.
        if knowledge:
            self._obtain_the_knowledge()

        if extension:



def ptpy_factory(transport, extension=None):
    # The order needs to be Transport inherits Extension inherits Base. This is
    # so that the extension can extend the base and the transport can
    # instantiate the correct endianness.
    inheritance = ((transport, extension, PTPDevice, object)
                   if extension is not None
                   else (transport, PTPDevice, object))
    return type('PTPy', inheritance, {})


# TODO: Add other transports?
transport = usb
# Attempt to instantiate simple device and get its information. Then terminate
# it.

PTPy = ptpy_factory(transport)
try:
    device = PTPy()
except PTPError:
    device = None

if device is not None:
    # TODO: Do this at each instantiation of PTPy instead of just once. This
    # workd OK for a single device but is not ideal.
    device_info = device.get_device_info()
    device._shutdown()
    try:
        extension = known_extensions[device_info.VendorExtensionID]
    except KeyError:
        extension = None

    PTPy = ptpy_factory(
        transport,
        extension
    )

# TODO: Add a raw option to get a pure PTP device, and default to a smart
# device that manages properties automatically.
