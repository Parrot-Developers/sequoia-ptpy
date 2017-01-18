'''Master module that instantiates the correct extension and transport.'''
from __future__ import absolute_import
from .extensions.canon import PTPDevice as canon
from .extensions.microsoft import PTPDevice as mtp
from .extensions.parrot import PTPDevice as parrot
from .ptp import PTPDevice, PTPError
from .transports.usb import USBTransport as usb

import os
import coloredlogs

# Set up full logging level when DEBUG is defined as in the environment
coloredlogs.install(
    level='DEBUG' if 'DEBUG' in os.environ else 'INFO',
    fmt='%(levelname)s %(asctime)s %(name)s[%(threadName)s] %(message)s'
)

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


def ptpy_factory(transport, extension=None):
    # The order needs to be Transport inherits Extension inherits Base. This is
    # so that the extension can extend the base and the transport can
    # instantiate the correct endianness.
    inheritance = ((transport, extension, PTPDevice, object)
                   if extension is not None
                   else (transport, PTPDevice, object))
    return type('PTPy', inheritance, {})


class PTPy(object):
    '''Class for all transports, extensions and basic PTP functionality'''
    def __new__(cls, device=None, extension=None, transport=None, knowledge=True, raw=False, **kwargs):
        '''Instantiate the correct class for a device automatically.'''
        # Determine transport
        if transport is None:
            # TODO: Implement discovery across transports once PTPIP is added.
            transport = usb

        # Determine extension
        if extension is None and not raw:
            plain = ptpy_factory(transport)
            try:
                plain_camera = plain()
            except PTPError:
                plain_camera = None

            if plain_camera is not None:
                device_info = plain_camera.get_device_info()
                plain_camera._shutdown()
                try:
                    extension = known_extensions[device_info.VendorExtensionID]
                except KeyError:
                    extension = None

        # Instantiate and construct.
        if raw:
            PTPy = ptpy_factory(transport)
        else:
            PTPy = ptpy_factory(
                transport,
                extension
            )
        # Query the device for information on all its properties and update
        # when there are changes.
        instance = PTPy(device)
        if knowledge and not raw:
            instance._obtain_the_knowledge()

        return instance

__all__ = (PTPy, PTPyError)
