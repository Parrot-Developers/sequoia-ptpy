#! /usr/bin/env python
from time import sleep, time
from .test_sequoia import TestSequoia
import pytest

# Verify that there are at least N images added after an InitiateCapture with N
# cameras activated. Do this for all combinations of activated sensors.
number_of_cameras = 5


# TODO: Put this function in a separate module of test helpers.
def initiate_capture(sequoia):
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


def set_valid_mask(sequoia, mask):
    '''Set PhotoSensorEnableMask. Return false when invalid.'''
    enable_response = sequoia.set_device_prop_value(
        'PhotoSensorEnableMask',
        sequoia._UInt32.build(mask)
    )
    # If the combination of enabled cameras is invalid, skip it.
    if enable_response.ResponseCode == 'InvalidDevicePropValue':
        return False
    # If the device is busy, try again ten times waiting a second.
    tries = 0
    while enable_response.ResponseCode != 'OK' and tries < 10:
        tries += 1
        sleep(1)
        enable_response = sequoia.set_device_prop_value(
            'PhotoSensorEnableMask',
            sequoia._UInt32.build(mask)
        )
    if enable_response.ResponseCode != 'OK':
        print(enable_response)
        assert enable_response.ResponseCode == 'OK', \
            'Could not set PhotoSensorEnableMask {}'.format(bin(mask))
    return True


def set_keep_on(sequoia, mask):
    '''Turn masked sensors on'''
    set_valid_mask(sequoia, mask)
    tries = 0
    keep_on = sequoia.get_device_prop_desc('PhotoSensorsKeepOn')
    while keep_on.CurrentValue != 1 and tries < 10:
        tries += 1
        sleep(1)
        sequoia.set_device_prop_value(
            'PhotoSensorsKeepOn',
            sequoia._UInt32.build(1)
        )
        keep_on = sequoia.get_device_prop_desc('PhotoSensorsKeepOn')
    assert keep_on.CurrentValue == 1, \
        'Could not turn sensors on after 10 tries (10 s).'


def unset_keep_on(sequoia):
    '''Turn masked sensors on'''
    tries = 0
    keep_on = sequoia.get_device_prop_desc('PhotoSensorsKeepOn')
    while keep_on.CurrentValue != 0 and tries < 10:
        tries += 1
        sleep(1)
        sequoia.set_device_prop_value(
            'PhotoSensorsKeepOn',
            sequoia._UInt32.build(0)
        )
        keep_on = sequoia.get_device_prop_desc('PhotoSensorsKeepOn')
    assert keep_on.CurrentValue == 0, \
        'Could not turn sensors off after 10 tries (10 s).'


class TestSequoiaEnableCapture(TestSequoia):
    def test_keep_on(self, sequoia):
        '''Verify a PhotoSensorsKeepOn does not block the Sequoia.'''
        with sequoia.session():
            set_keep_on(sequoia, 31)
            unset_keep_on(sequoia)

    def test_keep_on_capture(self, sequoia):
        '''Verify that a capture finishes with sensors on.'''

        with sequoia.session():

            # Capture image and wait for CaptureComplete
            set_keep_on(sequoia, 31)
            capture = initiate_capture(sequoia)

            tic = time()
            while True:
                evt = sequoia.event()
                if (
                        evt and
                        evt.EventCode == 'CaptureComplete' and
                        evt.TransactionID == capture.TransactionID
                ):
                    break
                assert time() - tic <= 40,\
                    'Waited for 40 seconds before giving up.\n'\
                    'No CaptureComplete received for InitiateCapture.'

            keep_on = sequoia.get_device_prop_desc('PhotoSensorsKeepOn')
            if keep_on.CurrentValue == 1:
                sequoia.set_device_prop_value(
                    'PhotoSensorsKeepOn',
                    sequoia._UInt32.build(0)
                )
                sleep(5)
            unset_keep_on(sequoia)

    @pytest.mark.parametrize(
        ('mask'),
        range(2**number_of_cameras),
    )
    def test_enable_capture(self, mask, sequoia):
        '''Verify that a capture with N enabled sensors poduces N images.'''

        with sequoia.session():
            keep_on = sequoia.get_device_prop_desc('PhotoSensorsKeepOn')
            if keep_on.CurrentValue == 1:
                sequoia.set_device_prop_value(
                    'PhotoSensorsKeepOn',
                    sequoia._UInt32.build(0)
                )

            # If mask is invalid, skip.
            if not set_valid_mask(sequoia, mask):
                return
            # Capture image and count the ObjectAdded events.
            capture = initiate_capture(sequoia)
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
                elif evt and evt.EventCode == 'CaptureComplete':
                    if not pytest.config.getoption('--ideal'):
                        pytest.skip('Use --ideal to check for non-PTP errors.')
                    assert acquired == expected,\
                        '{} images were expected than received. '\
                        'This is not a violation of PTP.'\
                        .format('More' if acquired < expected else 'Less')
                    return
                # Allow for sixty second delays in events... Though the
                # asynchronous event may take an indefinite amount of time,
                # anything longer than about ten seconds indicates there's
                # something wrong.
                assert time() - tic <= 40,\
                    'Waited for 40 seconds before giving up.\n'\
                    'No CaptureComplete received.\n'\
                    'Failed with {} images ({} ObjectAdded) for mask {} {} {}'\
                    .format(acquired, n_added, mask, hex(mask), bin(mask))
