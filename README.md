# Introduction

Pure Python implementation of the PTP standard as specified in
ISO15740:2013(E).

This implementation is transport agnostic and can be used along with USB,
serial or IP layers to communicate with PTP compliant cameras.

The entire codebase, tools and examples are compatible with both Python 3 and
Python 2.

[![Build Status](https://travis-ci.org/Parrot-Developers/sequoia-ptpy.svg?branch=master)](https://travis-ci.org/Parrot-Developers/sequoia-ptpy)

# Basic Usage

PTPy accomodates both the low-level developers wishing to test their PTP
implementation as well as users of the cameras in the market.

By default, PTPy will automatically detect which extension the camera supports
and load it so that the interaction is seamless.

> The most basic usage of PTPy with a camera connected is:

```python
from ptpy import PTPy

camera = PTPy()
print(camera.get_device_info())

with camera.session():
    camera.initiate_capture()
```

Developers might want to disable the extra functionality, or impose an
extension to use. E.g. when the PTP Extension ID has not been assigned.

> It is possible to get bare PTP functionality with:

```python
from ptpy import PTPy

camera = PTPy(raw=True)
print(camera.get_device_info())

with camera.session():
    # Do basic things here.
```

A developer might want to test the case where the extension is incorrectly
identified. This is possible by imposing an arbitrary extension.

> Impose MTP (Microsoft PTP Extension) to any camera:

```python
from ptpy import PTPy
from ptpy.extensions.microsoft import PTPDevice as mtp

camera = PTPy(extension=mtp)
with camera.session():
    # Do bizarre things here.
```

Sessions are managed automatically with context managers.
All sessions under a top session with share the top session.

> To inspect the current session and transaction use the corresponding properties:

```python
from ptpy import PTPy

camera = PTPy()
with camera.session():
    camera.get_device_info()

    print('Top level session:')
    print(camera.session_id)
    print('Transaction ID:')
    print(camera.transaction_id)

    with camera.session():

        camera.get_device_info()

        print('Shared session:')
        print(camera.session_id)

        print('Transaction ID increases:')
        print(camera.transaction_id)

with camera.session():
    camera.get_device_info()

    print('First session:')
    print(camera.session_id)

    print('Transaction ID:')
    print(camera.transaction_id)

with camera.session():
    camera.get_device_info()

    print('Second session:')
    print(camera.session_id)

    print('Transaction ID:')
    print(camera.transaction_id)
```

# Transports

## USB
A proof-of-concept USB implementation is provided using PyUSB. Though it might
not work with all USB controllers in cameras today. In some operating systems,
it might be necessary to be `root` in order to access USB devices directly.

For the USB transport, the `_shutdown` method is provided to explicitly release
the USB interface. At the end of the Python interpreter session this will happen
automatically.

## IP
A proof-of-concept PTP/IP implementation is provided using sockets. Since there
is no device discovery implemented yet, the address must be provided directly.

```python
from ptpy import PTPy
from ptpy.transports.ip import IPTransport

# Default PTP/IP port assumed
c = PTPy(transport=IPTransport, device='197.168.47.1')

# Optionally:
c = PTPy(transport=IPTransport, device=('197.168.47.1', 15740))
```

# Extensions

## State of the art

Full support for the Parrot Drone SAS extension is provided. Extensions are
meant to provice vendor-specific sets of operations, events and properties.

Partial support for Canon, Microsoft (MTP), and Nikon extensions is provided.
Full support is expected eventually.

Canon and Nikon extensions integrate their specific events mechanisms.

Extensions are managed automatically for users or can be imposed by developers.

## Framework

A developer can take any of the sample extensions as a model for others.

In general extensions do not need to overwrite any base PTP operations, events
or properties. Indeed most extensions will add some extra commands.

# Installing

To install issue `pip install .` or `pip install -e .` for developer mode. The
command `python setup.py install` should also work.

# Development

## Requirements

A `requirements.txt` file is provided for ease of development.
For developing tests, an additional `tests/requirements.txt` is provided.

Under Windows, install `libusb` or `libusb-win32` using
[zadig](http://zadig.akeo.ie).

## Tests

Vendors might want to test their devices against the hardware tests. These
become immediately accessible when a camera is connected.

To launch tests issue `python setup.py test`.

A convenience Makefile is provided so the command becomes `make test`.

All tests are implemented using `py.test`, which can also be called directly:
`py.test ./tests`

# TODO

- Implement extension mapped codes from PTP1.1
