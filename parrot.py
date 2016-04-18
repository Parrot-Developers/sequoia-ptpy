'''This module extends PTPDevice for Parrot devices.

Use it in a master module that determines the vendor and automatically uses its
extension:

    from ptp import *
    # Here PTPDevice is unextended
    from vendors.parrot import *
    # Here PTPDevice has a vendor extension
    from transport.usb import *
    # Here PTPDevice can now be instantiated over transport
'''
import ptp

__all__ = ('OperationCode', 'ResponseCode', 'EventCode', 'PTPDevice',)


def DeviceProperty(_be_=False, _le_=False, **product_properties):
    return ptp.DeviceProperty(
        _be_=_be_, _le_=_le_,
        PhotoSensorEnableMask=0xD201,
        PhotoSensorsKeepOn=0xD202,
        MultispectralImageSize=0xD203,
        MainBitDepth=0xD204,
        MultispectralBitDepth=0xD205,
        HeatingEnable=0xD206,
        WifiStatus=0xD207,
        WifiSSID=0xD208,
        WifiEncryptionType=0xD209,
        WifiPassphrase=0xD20A,
        WifiChannel=0xD20B,
        Localization=0xD20C,
        WifiMode=0xD20D,
        AntiFlickeringFrequency=0xD210,
        DisplayOverlayMask=0xD211,
        GPSInterval=0xD212,
        MultisensorsExposureMeteringMode=0xD213,
        MultisensorsExposureTime=0xD214,
        MultisensorsExposureProgramMode=0xD215,
        MultisensorsExposureIndex=0xD216,
        **product_properties
    )


def OperationCode(_be_=False, _le_=False, **product_operations):
    return ptp.OperationCode(
        _be_=_be_, _le_=_le_,
        GetSunshineValues=0x9201,
        GetTemperatureValues=0x9202,
        GetAngleValues=0x9203,
        GetGpsValues=0x9204,
        GetGyroscopeValues=0x9205,
        GetAccelerometerValues=0x9206,
        GetMagnetometerValues=0x9207,
        GetImuValues=0x9208,
        GetStatusMask=0x9209,
        EjectStorage=0x920A,
        StartMagnetoCalib=0x9210,
        StopMagnetoCalib=0x9211,
        MagnetoCalibStatus=0x9212,
        SendFirmwareUpdate=0x9213,
        **product_operations
    )


def ResponseCode(_be_=False, _le_=False, **product_responses):
    return ptp.ResponseCode(
        _be_=_be_, _le_=_le_,
        **product_responses
    )


def EventCode(_be_=False, _le_=False, **product_events):
    return ptp.EventCode(
        _be_=_be_, _le_=_le_,
        Status=0xC201,
        MagnetoCalibrationStatus=0xC202,
        **product_events
    )


class PTPDevice(ptp.PTPDevice):
    '''This class implements Parrot's PTP operations.'''
