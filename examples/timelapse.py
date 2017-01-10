#!/usr/bin/env python
from ptpy import PTPy
from argparse import ArgumentParser
from time import time, sleep

parser = ArgumentParser()
parser.add_argument(
    '-t',
    type=float,
    help='Time between captures in seconds. Default is 0.1 seconds.'
)
parser.add_argument(
    '-n',
    type=int,
    help='Number of captures. Negative numbers mean "forever" (default)'
)
args = parser.parse_args()

camera = PTPy()
with camera.session():
    successful = 0
    beginning = time()
    while True if args.n is None or args.n < 0 else successful < args.n:
        capture = camera.initiate_capture()
        if capture.ResponseCode == 'OK':
            successful += 1
            cumulative_rate = (time() - beginning) / (successful)
            print('elapsed {:.2f}s cumulative rate {:.2f}s captured {}'.format(
                time() - beginning,
                cumulative_rate,
                successful
            ))
            sleep(.1 if args.t is None else args.t)
