#!/usr/bin/env python
import ptpy
from ptpy.transports.usb import find_usb_cameras
from threading import Thread, Event
import sys
import logging
from rainbow_logging_handler import RainbowLoggingHandler
from time import sleep, time

# Set up log
log = logging.getLogger('Live')
formatter = logging.Formatter(
    '%(levelname).1s '
    '%(relativeCreated)d '
    '%(name)s'
    '[%(threadName)s] '
    '%(message)s'
)
handler = RainbowLoggingHandler(
    sys.stderr,
)
level = 'INFO'
log.setLevel(level)
handler.setFormatter(formatter)
log.addHandler(handler)

# Set up threads and events
finished = Event()


def capture_thread(camera):
    '''Initiate captures regularly for camera'''
    with camera.session():
        info = camera.get_device_info()
        while not finished.is_set():
            capture = camera.initiate_capture()
            if capture.ResponseCode == 'OK':
                log.info(
                    '{}: successfully initiated capture'
                    .format(info.SerialNumber)
                )
            sleep(.1)


def download_thread(camera):
    '''Download all non-folders in events from camera'''
    with camera.session():
        caminfo = camera.get_device_info()
        while not finished.is_set():
            event = camera.event()
            if event and event.EventCode == 'ObjectAdded':
                handle = event.Parameter[0]
                info = camera.get_object_info(handle)
                # Download all things that are not groups of other things.
                if info.ObjectFormat != 'Association':
                    log.info(
                        '{}: downloading {}'
                        .format(caminfo.SerialNumber, info.Filename)
                    )
                    tic = time()
                    obj = camera.get_object(handle)
                    toc = time()
                    log.info('{}: {:.1f}MB/s'.format(
                        caminfo.SerialNumber,
                        len(obj.Data) / ((toc - tic) * 1e6))
                    )
                    with open(info.Filename, mode='w') as f:
                        f.write(obj.Data)


# Find each connected USB camera try to instantiate it and set up a capture and
# download thread for it if successful.
threads = []
for i, device in enumerate(find_usb_cameras()):

    try:
        camera = ptpy.PTPy(device=device)
        info = camera.get_device_info()
        caminfo = (info.Manufacturer, info.Model, info.SerialNumber)
        if (
                'InitiateCapture' not in info.OperationsSupported or
                'GetObject' not in info.OperationsSupported
        ):
            raise Exception(
                '{} {} {} does not support capture or download...'
                .format(*caminfo)
            )
        log.info(
            'Found {} {} {}'
            .format(*caminfo)
        )
    except Exception as e:
        log.error(e)
        continue

    capture = Thread(
        name='PHOTO{:02}'.format(i),
        target=capture_thread,
        args=(camera,)
    )
    threads.append(capture)

    download = Thread(
        name='DWNLD{:02}'.format(i),
        target=download_thread,
        args=(camera,)
    )
    threads.append(download)

for thread in threads:
    thread.start()

# Let the threads run for 30 seconds.
sleep(30)
finished.set()

# Wait for them to finish running.
for thread in threads:
    if thread.is_alive():
        thread.join()
