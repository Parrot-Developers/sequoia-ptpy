#! /usr/bin/env python
from ptpy.usb_transport import USBTransport, find_usb_cameras
# TODO: Fix import once ptpy module is better structured.
from time import sleep, time
import pytest

devs = find_usb_cameras()

sequoia = None
for dev in devs:
    camera = USBTransport(dev)
    device_info = camera.get_device_info()
    if 'Sequoia' in device_info.Model:
        sequoia = camera
        break


# Verify that there are at least N images added after an InitiateCapture with N
# cameras activated. Do this for all combinations of activated sensors.
number_of_cameras = 5


def initiate_capture():
    '''Initiate capture.'''
    capture_response = sequoia.initiate_capture()
    # If the device is doing something else, try again ten times waiting a
    # second.
    tries = 0
    while capture_response.ResponseCode != 'OK' and tries < 10:
        tries += 1
        sleep(1)
        capture_response = sequoia.initiate_capture()
    if capture_response.ResponseCode != 'OK':
        print(capture_response)
        assert capture_response.ResponseCode == 'OK', \
            'Could not initiate capture after 10 tries.'
    return capture_response


def set_valid_mask(mask):
    '''Set PhotoSensorEnableMask. Return false when invalid.'''
    enable_response = sequoia.set_device_prop_value(
        'PhotoSensorEnableMask',
        sequoia._UInt32('Mask').build(mask)
    )
    # If the combination of enabled cameras is invalid, skip it.
    if enable_response.ResponseCode == 'InvalidDevicePropValue':
        print('{} is an invalid mask. Skipping it.'.format(bin(mask)))
        return False
    # If the device is busy, try again ten times waiting a second.
    tries = 0
    while enable_response.ResponseCode != 'OK' and tries < 10:
        tries += 1
        sleep(1)
        enable_response = sequoia.set_device_prop_value(
            'PhotoSensorEnableMask',
            sequoia._UInt32('Mask').build(mask)
        )
    if enable_response.ResponseCode != 'OK':
        print(enable_response)
        assert enable_response.ResponseCode == 'OK', \
            'Could not set PhotoSensorEnableMask {}'.format(bin(mask))
    return True


@pytest.mark.parametrize(
    ('mask'),
    range(2**number_of_cameras),
)
def test_enable_capture(mask):
    '''Verify that a capture with N enabled sensors poduces N images.'''
    if sequoia is None:
        return

    with sequoia.session():
        print('Testing capture for mask {}'.format(bin(mask)))

        # If mask is invalid, skip.
        if not set_valid_mask(mask):
            return
        # Capture image and count the ObjectAdded events.
        capture = initiate_capture()
        acquired = 0
        n_added = 0
        expected = bin(mask).count('1')
        tic = time()
        while acquired < expected:
            # Check events
            evt = sequoia.event()
            # If object added verify is it is an image
            if (
                    evt and
                    evt.TransactionID == capture.TransactionID and
                    evt.EventCode == 'ObjectAdded'
            ):
                n_added += 1
                info = sequoia.get_object_info(evt.Parameter[0])
                if (
                        info and
                        ('TIFF' in info.ObjectFormat or
                         'EXIF_JPEG' in info.ObjectFormat)
                ):
                    acquired += 1
            # Otherwise if the capture is complete, tally up.
            elif evt and evt.EventCode == 'CaptureCompleted':
                assert acquired < expected,\
                    'More images were expected than received.'
                return
            # Allow for one-minute delays in events... Though the
            # asynchronous event may take an indefinite amount of time,
            # anything longer than about ten seconds indicates there's
            # something wrong.
            assert time() - tic <= 60,\
                'Waited for 1 minute before giving up. '\
                'Failed with {} ({} ObjectAdded) images for mask {}'\
                .format(acquired, n_added, bin(mask))
