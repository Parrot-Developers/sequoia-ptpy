#!/usr/bin/env python
import ptpy

camera = ptpy.PTPy()
with camera.session():
    capture = camera.initiate_capture()
