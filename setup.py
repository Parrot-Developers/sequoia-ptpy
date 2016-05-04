import os
from setuptools import setup, find_packages
from pip.req import parse_requirements


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

install_requirements = [
    str(r.req) for r in parse_requirements('requirements.txt', session=False)
]

test_requirements = [
    str(r.req) for r in parse_requirements('tests/requirements.txt', session=False)
]

setup(
    name='ptpy',
    version='0.0.0',
    description='A pure Python implementation of Picture Transfer Protocol.',
    long_description=read('README.md'),
    packages=find_packages(exclude=['tests', 'examples']),
    keywords='ptp mtp usb ip ptpip ptpusb parrot canon nikon microsoft',
    author='Luis Mario Domenzain',
    author_email='ld@airinov.fr',
    install_requires=install_requirements,
    tests_require=test_requirements,
)
