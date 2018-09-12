import os
from setuptools import setup, find_packages


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


setup(
    author_email='luis.domenzain@parrot.com',
    author='Luis Mario Domenzain',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Home Automation',
        'Topic :: Multimedia',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Capture',
        'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Filesystems',
        'Topic :: System :: Hardware',
        'Topic :: System :: Hardware :: Hardware Drivers',
    ],
    description='A pure Python implementation of Picture Transfer Protocol.',
    install_requires=read('requirements.txt'),
    keywords='ptp mtp usb ip ptpip ptpusb parrot canon nikon microsoft',
    license='BSD-3-Clause',
    long_description=read('README.md'),
    name='ptpy',
    packages=find_packages(exclude=['tests', 'examples']),
    setup_requires=['pytest-runner'],
    tests_require=read('tests/requirements.txt'),
    url='https://github.com/Parrot-Developers/sequoia-ptpy',
    version='0.3.3',
)
