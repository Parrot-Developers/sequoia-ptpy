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

__all__ = ('PTPDevice',)


class PTPDevice(ptp.PTPDevice):
    '''This class implements Parrot's PTP operations.'''

    def _PropertyCode(self, **product_properties):
        return ptp.PTPDevice._PropertyCode(
            self,
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

    def _OperationCode(self, **product_operations):
        return ptp.PTPDevice._OperationCode(
            self,
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

    def _ResponseCode(self, **product_responses):
        return ptp.PTPDevice._ResponseCode(
            self,
            **product_responses
        )

    def _EventCode(self, **product_events):
        return ptp.PTPDevice._EventCode(
            self,
            Status=0xC201,
            MagnetoCalibrationStatus=0xC202,
            **product_events
        )

    def _FilesystemType(self, **product_filesystem_types):
        return ptp.PTPDevice._ResponseCode(
            self,
            **product_filesystem_types
        )
