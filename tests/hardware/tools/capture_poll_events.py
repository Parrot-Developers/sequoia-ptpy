#!/usr/bin/env python
from ptpy import PTPy

camera = PTPy()
with camera.session():
    print('Initiating capture')
    print(camera.initiate_capture())
    while True:
        evt = camera.event()
        if evt:
            print(evt)
