import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='ptpy',
    version='0.0.0',
    description='A pure Python implementation of Picture Transfer Protocol.',
    long_description=read('README.md'),
    packages=find_packages(exclude=['tests', 'examples']),
    keywords='ptp mtp usb ip ptpip ptpusb parrot canon nikon microsoft',
    author='Luis Mario Domenzain',
    author_email='ld@airinov.fr',
)
