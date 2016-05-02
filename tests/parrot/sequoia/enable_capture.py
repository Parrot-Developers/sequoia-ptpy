#! /usr/bin/env python
from ptpy.usb_transport import USBTransport, find_usb_cameras
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

for mask in tqdm(range(2**number_of_cameras)):
    enable_response = sequoia.set_device_prop_value(
        'PhotoSensorEnableMask',
        sequoia._UInt32('Mask').build(mask)
    )
    # If the combination of enabled cameras is invalid, skip it.
    if enable_response.ResponseCode == 'InvalidDevicePropValue':
        tqdm.write('{} is an invalid mask. Skipping it.'.format(bin(mask)))
        continue
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
        raise Exception(
            'Could not set PhotoSensorEnableMask {}'
            .format(bin(mask))
        )

    # Capture image and count the ObjectAdded events.
    sequoia.initiate_capture()
    acquired = 0
    expected = bin(mask).count('1')
    tic = time()
    while acquired < expected:
        evt = sequoia.event()
        if evt and evt.EventCode == 'ObjectAdded':
            info = sequoia.get_object_info(evt.Parameter[0])
            if 'TIFF' in info.ObjectFormat or 'EXIF_JPEG' in info.ObjectFormat:
                acquired += 1
        elif evt:
            tqdm.write('Received event {}'.format(evt.EventCode))
        # Allow for one minute delays in events...
        if time() - tic > 60:
            raise Exception(
                'Waited for 1 minute before giving up. '
                'Failed with {} images for mask {}'.format(acquired, bin(mask))
            )
    tqdm.write(
        'Received {} images for mask {}'
        .format(acquired, bin(mask))
    )
