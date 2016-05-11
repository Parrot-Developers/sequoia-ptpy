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

Full support for the Parrot Drone SAS extension is provided. Extensions are
meant to provice vendor-specific sets of operations, events and properties.

Partial support for Canon and Microsoft (MTP) extensions is provided. Full
support is expected eventually.

In general these do not need to overwrite any base PTP operations, events or
properties.

# Requirements

A `requirements.txt` file is provided for ease of development.

# Tests

Vendors might want to test their devices against the hardware tests. These
become immediately accessible when a camera is connected.

To launch tests issue `python setup.py test`.

# Installing

To install issue `pip install .` or `pip install -e .` for developer mode. The
command `python setup.py install` should also work.

# TODO

- Rearrage classes so transport and extensions can be inherited separately and
  in any order
- Write top-level class to deal with extensions automatically from
  `device_info`
- Implement extension mapped codes from PTP1.1
