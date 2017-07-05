'''Master module that instantiates the correct extension and transport.'''
from __future__ import absolute_import
from .extensions.canon import Canon
from .extensions.microsoft import Microsoft
from .extensions.parrot import Parrot
from .extensions.nikon import Nikon
from .ptp import PTPError
from .ptp import PTP
from .transports.usb import USBTransport as usb

import os
import coloredlogs
import logging

logger = logging.getLogger(__name__)

# Set up full logging level when DEBUG is defined as in the environment
coloredlogs.install(
    level='DEBUG' if 'PTPY_DEBUG' in os.environ else 'INFO',
    fmt='%(levelname)s %(asctime)s %(name)s[%(threadName)s] %(message)s',
    )
if 'PTPY_DEBUG_LOG' in os.environ:
    logger.addHandler(logging.FileHandler(os.environ['PTPY_DEBUG_LOG']))


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
    'Microsoft': Microsoft,
    'Equinox': None,
    'Viewquest': None,
    'STMicroelectronics': None,
    'Nikon': Nikon,
    'Canon': Canon,
    'FotoNation': None,
    'PENTAX': None,
    'Fuji': None,
    'Sony': None,
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
            transport = usb

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
                    # TODO: Check vendor and product for non-compliant
                    # cameras.
                    extension = known_extensions[device_info.VendorExtensionID]
                except KeyError:
                    extension = None

        # Instantiate and construct.
        if raw:
            logger.debug('Raw PTP only')
            PTPy = ptpy_factory(transport)
        else:
            logger.debug('Imposing {} extension'.format(extension))
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

    def __init__(self, *args, **kwargs):
        logger.debug('Init PTPy')
        super(PTPy, self).__init__(*args, **kwargs)


__all__ = (PTPy, PTPyError)
