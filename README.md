# Introduction

Pure Python implementation of the PTP standard as specified in
ISO15740:2013(E).

This implementation is transport agnostic and can be used along with USB,
serial or IP layers to communicate with PTP compliant cameras.

# Transport

A proof-of-concept USB implementation is provided using PyUSB. Though it might
not work with all USB controllers in cameras today. In some operating systems,
it might be necessary to be `root` in order to access USB devices directly.

# Extensions

## State of the art

Full support for the Parrot Drone SAS extension is provided. Extensions are
meant to provice vendor-specific sets of operations, events and properties.

Partial support for Canon and Microsoft (MTP) extensions is provided. Full
support is expected eventually.

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
For developing tests, a separate `tests/requirements.txt` is provided.

## Tests

Vendors might want to test their devices against the hardware tests. These
become immediately accessible when a camera is connected.

To launch tests issue `python setup.py test`.

A convenience Makefile is provided so the command becomes `make test`.

All tests are implemented using `py.test`, which can also be called directly:
`py.test ./tests`

# TODO

- Implement extension mapped codes from PTP1.1
