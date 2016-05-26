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
from construct import (
    BitStruct, Container, Enum, ExprAdapter, Flag, Padding, Pass
)

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
            MultisensorsIrradianceGain=0xD217,
            MultisensorsIrradianceIntegrationTime=0xD218,
            OverlapRate=0xD219,
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
        return ptp.PTPDevice._FilesystemType(
            self,
            **product_filesystem_types
        )

    def _Sunshine(self):
        return ExprAdapter(
            self._PTPArray('Sunshine', self._UInt32('Int')),
            encoder=lambda obj, ctx: [
                obj.Green, obj.Red, obj.RedEdge, obj.NIR,
            ],
            decoder=lambda obj, ctx: Container(
                Green=obj[0], Red=obj[1], RedEdge=obj[2], NIR=obj[3],
            ),
        )

    def _Temperature(self):
        return ExprAdapter(
            self._PTPArray('Temperature', self._Int32('Int')),
            encoder=lambda obj, ctx: [
                obj.P7, obj.P7MU, obj.DDR. obj.WiFi, obj.IMU, obj.IMUSunshine
            ],
            decoder=lambda obj, ctx: Container(
                P7=obj[0], P7MU=obj[1], DDR=obj[2],
                WiFi=obj[3], IMU=obj[4], IMUSunshine=obj[5],
            ),
        )

    def _Angle(self):
        return ExprAdapter(
            self._PTPArray('Angle', self._UInt32('Int')),
            encoder=lambda obj, ctx: [obj.Yaw, obj.Pitch, obj.Roll],
            decoder=lambda obj, ctx: Container(
                Yaw=obj[0], Pitch=obj[1], Roll=obj[2]
            ),
        )

    def _GPS(self):
        return ExprAdapter(
            self._PTPArray('GPS', self._UInt32('Int')),
            encoder=lambda obj, ctx: [
                obj.Longitude.Deg, obj.Longitude.Min, obj.Longitude.Sec,
                obj.Latitude.Deg, obj.Latitude.Min, obj.Latitude.Sec,
                obj.Altitude,
            ],
            decoder=lambda obj, ctx: Container(
                Longitude=Container(Deg=obj[0], Min=obj[1], Sec=obj[2]),
                Latitude=Container(Deg=obj[3], Min=obj[4], Sec=obj[5]),
                Altitude=obj[6]
            ),
        )

    def _Gyroscope(self):
        return ExprAdapter(
            self._PTPArray('Gyroscope', self._UInt32('Int')),
            encoder=lambda obj, ctx: [obj.X, obj.Y, obj.Z],
            decoder=lambda obj, ctx: Container(
                X=obj[0], Y=obj[1], Z=obj[2],
            ),
        )

    def _Accelerometer(self):
        return ExprAdapter(
            self._PTPArray('Accelerometer', self._UInt32('Int')),
            encoder=lambda obj, ctx: [obj.X, obj.Y, obj.Z],
            decoder=lambda obj, ctx: Container(
                X=obj[0], Y=obj[1], Z=obj[2],
            ),
        )

    def _Magnetometer(self):
        return ExprAdapter(
            self._PTPArray('Magnetometer', self._UInt32('Int')),
            encoder=lambda obj, ctx: [obj.X, obj.Y, obj.Z],
            decoder=lambda obj, ctx: Container(
                X=obj[0], Y=obj[1], Z=obj[2],
            ),
        )

    def _IMU(self):
        return ExprAdapter(
            self._PTPArray('IMU', self._UInt32('Int')),
            encoder=lambda obj, ctx: [
                obj.Gyroscope.X,
                obj.Gyroscope.Y,
                obj.Gyroscope.Z,
                obj.Accelerometer.X,
                obj.Accelerometer.Y,
                obj.Accelerometer.Z,
                obj.Magnetometer.X,
                obj.Magnetometer.Y,
                obj.Magnetometer.Z,
                obj.Angle.Yaw,
                obj.Angle.Pitch,
                obj.Angle.Roll,
            ],
            decoder=lambda obj, ctx: Container(
                Gyroscope=Container(X=obj[0], Y=obj[1], Z=obj[2]),
                Accelerometer=Container(X=obj[3], Y=obj[4], Z=obj[5]),
                Magnetometer=Container(X=obj[6], Y=obj[7], Z=obj[8]),
                Angle=Container(Yaw=obj[9], Pitch=obj[10], Roll=obj[11]),
            ),
        )

    def _Status(self):
        return BitStruct(
            'Status',
            Flag('CameraRunning'),
            Flag('MainImuCalibRunning'),
            Flag('AuxiliaryImuCalibRunning'),
            Flag('AuxiliaryConnected'),
            Flag('GpsRunning'),
            Flag('RemoteGpsRunning'),
            Flag('CamNumber01Error'),
            Flag('CamNumber02Error'),
            Flag('CamNumber03Error'),
            Flag('CamNumber04Error'),
            Flag('CamNumber05Error'),
            Flag('CamNumber06Error'),
            Flag('CamNumber07Error'),
            Flag('CamNumber08Error'),
            Flag('CamNumber09Error'),
            Flag('CamNumber10Error'),
            Flag('CamNumber11Error'),
            Flag('CamNumber12Error'),
            Flag('CamNumber13Error'),
            Flag('CamNumber14Error'),
            Flag('CamNumber15Error'),
            Flag('CamNumber16Error'),
            # If new flags are defined, the padding should be asjusted.
            Padding(10),
        )

    def _MagnetoStatus(self):
        return Enum(
            self._UInt32('MagnetoStatus'),
            CalibrationOk=1,
            CalibrationRunning=2,
            CalibrationRollPending=3,
            CalibrationPitchPending=4,
            CalibrationYawPending=5,
            CalibrationFailed=6,
            CalibrationAborted=7,
            _default_=Pass,
        )

    def _set_endian(self, little=False, big=False):
        ptp.PTPDevice._set_endian(
            self,
            little=False,
            big=False
        )
        self._Sunshine = self._Sunshine()
        self._Temperature = self._Temperature()
        self._Angle = self._Angle()
        self._GPS = self._GPS()
        self._Gyroscope = self._Gyroscope()
        self._Accelerometer = self._Accelerometer()
        self._Magnetometer = self._Magnetometer()
        self._IMU = self._IMU()
        self._Status = self._Status()
        self._MagnetoStatus = self._MagnetoStatus()

    def get_sunshine_values(self):
        ptp = Container(
            OperationCode='GetSunshineValues',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._Sunshine)

    def get_temperature_values(self):
        ptp = Container(
            OperationCode='GetTemperatureValues',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._Temperature)

    def get_angle_values(self, imu_id=0):
        ptp = Container(
            OperationCode='GetAngleValues',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._Angle)

    def get_gps_values(self):
        ptp = Container(
            OperationCode='GetGpsValues',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._GPS)

    def get_gyroscope_values(self, imu_id=0):
        ptp = Container(
            OperationCode='GetGyroscopeValues',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._Gyroscope)

    def get_accelerometer_values(self, imu_id=0):
        ptp = Container(
            OperationCode='GetAccelerometerValues',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._Accelerometer)

    def get_magnetometer_values(self, imu_id=0):
        ptp = Container(
            OperationCode='GetMagnetometerValues',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._Magnetometer)

    def get_imu_values(self, imu_id=0):
        ptp = Container(
            OperationCode='GetImuValues',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._IMU)

    def get_status_mask(self, imu_id=0):
        ptp = Container(
            OperationCode='GetStatusMask',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._Status)

    def eject_storage(self, storage_id):
        ptp = Container(
            OperationCode='EjectStorage',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[storage_id]
        )
        return self.mesg(ptp)

    def start_magneto_calib(self, imu_id=0):
        ptp = Container(
            OperationCode='StartMagnetoCalib',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[imu_id]
        )
        return self.mesg(ptp)

    def stop_magneto_calib(self, imu_id=0):
        ptp = Container(
            OperationCode='StopMagnetoCalib',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[imu_id]
        )
        return self.mesg(ptp)

    def get_magneto_calib_status(self, imu_id=0):
        ptp = Container(
            OperationCode='MagnetoCalibStatus',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self.__parse_if_data(response, self._MagnetoStatus)

    def send_firmware(self, firmware):
        ptp = Container(
            OperationCode='SendFirmwareUpdate',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        return self.send(ptp, firmware)
