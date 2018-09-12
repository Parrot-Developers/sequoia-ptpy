'''Master module that instantiates the correct extension and transport.'''
from __future__ import absolute_import
from .extensions.canon import Canon
from .extensions.microsoft import Microsoft
from .extensions.parrot import Parrot
from .extensions.nikon import Nikon
from .extensions.sony import Sony
from .ptp import PTP, PTPError
from .transports.usb import USBTransport as USB
from .transports.ip import IPTransport as IP

import os
import sys
import logging
from rainbow_logging_handler import RainbowLoggingHandler

# Set up logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(levelname).1s '
    '%(relativeCreated)d '
    '%(name)s'
    '[%(threadName)s:%(funcName)s:%(lineno)s] '
    '%(message)s'
)
handler = RainbowLoggingHandler(
    sys.stderr,
)
level = 'DEBUG' if 'PTPY_DEBUG' in os.environ else 'INFO'

logger.setLevel(level)
handler.setFormatter(formatter)
logger.addHandler(handler)
if 'PTPY_DEBUG_LOG' in os.environ:
    logger.addHandler(logging.FileHandler(os.environ['PTPY_DEBUG_LOG']))

__all__ = (
    # Extensions
    'Canon',
    'Microsoft',
    'Nikon',
    'Sony',
    # Transports
    'IP',
    'USB',
    # Classes and errors
    'PTPError',
    'PTPy',
)

# As extensions are implemented, they should be added here, so they are
# automatically used. The names here need to match those in ptp.py
# VendorExtensionID.
known_extensions = {
    'EastmanKodak': None,
    'SeikoEpson': None,
    'Agilent': None,
    'Polaroid': None,
    'AgfaGevaert': None,
    'Microsoft': Microsoft,
    'Equinox': None,
    'Viewquest': None,
    'STMicroelectronics': None,
    'Nikon': Nikon,
    'Canon': Canon,
    'FotoNation': None,
    'PENTAX': None,
    'Fuji': None,
    'Sony': Sony,
    'Samsung': None,
    'Parrot': Parrot,
}


def ptpy_factory(transport, extension=None):
    # The order needs to be Transport inherits Extension inherits Base. This is
    # so that the extension can extend the base and the transport can
    # instantiate the correct endianness.
    inheritance = ((extension, PTP, transport)
                   if extension is not None
                   else (PTP, transport))
    return type('PTPy', inheritance, {})


def choose_extension(device_info):

    if 'Canon' in device_info.Manufacturer:
        return Canon
    elif 'Nikon' in device_info.Manufacturer:
        return Nikon
    else:
        return known_extensions[device_info.VendorExtensionID]


class PTPy(object):
    '''Class for all transports, extensions and basic PTP functionality'''
    def __new__(cls, device=None, extension=None, transport=None,
                knowledge=True, raw=False, **kwargs):
        '''Instantiate the correct class for a device automatically.'''
        # Determine transport
        logger.debug('New PTPy')
        if transport is None:
            logger.debug('Determining available transports')
            # TODO: Implement discovery across transports once PTPIP is added.
            transport = USB

        # Determine extension
        if extension is None and not raw:
            plain = ptpy_factory(transport)
            try:
                plain_camera = plain(device=device)
            except PTPError:
                plain_camera = None

            if plain_camera is not None:
                device_info = plain_camera.get_device_info()
                plain_camera._shutdown()
                try:
                    extension = choose_extension(device_info)
                except KeyError:
                    pass

        # Instantiate and construct.
        if raw:
            logger.debug('Raw PTP only')
            PTPy = ptpy_factory(transport)
        else:
            logger.debug('Imposing {} extension'.format(extension))
            if extension is None:
                logger.warning('Could not choose camera extension')
            PTPy = ptpy_factory(
                transport,
                extension
            )
        # Query the device for information on all its properties and update
        # when there are changes.
        instance = PTPy(device=device)
        if knowledge and not raw:
            instance._obtain_the_knowledge()

        return instance

    def __init__(self, *args, **kwargs):
        logger.debug('Init PTPy')
        super(PTPy, self).__init__(*args, **kwargs)
