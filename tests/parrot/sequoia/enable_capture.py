#! /usr/bin/env python
from ptpy.usb_transport import USBTransport, find_usb_cameras
# TODO: Fix import once ptpy module is better structured.
from time import sleep, time
from tqdm import tqdm

devs = find_usb_cameras()

for dev in devs:
    sequoia = USBTransport(dev)
    device_info = sequoia.get_device_info()
    if 'Sequoia' in device_info.Model:
        break
else:
    raise Exception('No available Sequoia found through PTP.')


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
        tqdm.write(str(capture_response))
        raise Exception('Could not InitiateCapture')


def set_valid_mask(mask):
    '''Set PhotoSensorEnableMask. Return false when invalid.'''
    enable_response = sequoia.set_device_prop_value(
        'PhotoSensorEnableMask',
        sequoia._UInt32('Mask').build(mask)
    )
    # If the combination of enabled cameras is invalid, skip it.
    if enable_response.ResponseCode == 'InvalidDevicePropValue':
        tqdm.write('{} is an invalid mask. Skipping it.'.format(bin(mask)))
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
        tqdm.write(str(enable_response))
        raise Exception(
            'Could not set PhotoSensorEnableMask {}'
            .format(bin(mask))
        )
    return True

with sequoia.session():
    for mask in tqdm(range(2**number_of_cameras), unit='test'):
        tqdm.write('-------------------------------------------------')
        tqdm.write('Testing capture for mask {}'.format(bin(mask)))

        # If mask is invalid, skip.
        if not set_valid_mask(mask):
            continue
        # Capture image and count the ObjectAdded events.
        initiate_capture()
        acquired = 0
        n_added = 0
        expected = bin(mask).count('1')
        tic = time()
        failed = False
        while acquired < expected:
            # Check events
            evt = sequoia.event()
            # If object added verify is it is an image
            if evt and evt.EventCode == 'ObjectAdded':
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
                failed = acquired < expected
                break
            # Allow for one-minute delays in events... Though the asynchronous
            # event may take an indefinite amount of time, anything longer than
            # about ten seconds indicates there's something wrong.
            if time() - tic > 60:
                failed = True
                break
        if failed:
            tqdm.write(
                'Waited for 1 minute before giving up. '
                'Failed with {} ({} ObjectAdded) images for mask {}'
                .format(acquired, n_added, bin(mask))
            )
        else:
            tqdm.write(
                'Success: {} images for mask {}'
                .format(acquired, bin(mask))
            )
