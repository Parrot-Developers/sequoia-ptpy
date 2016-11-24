#!/usr/bin/env python
from ptpy import PTPy

camera = PTPy()
with camera.session():
    while True:
        evt = camera.event()
        if evt:
            print(evt)
