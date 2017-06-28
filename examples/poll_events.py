#!/usr/bin/env python
import ptpy

camera = ptpy.PTPy()
with camera.session():
    while True:
        evt = camera.event()
        if evt:
            print(evt)
