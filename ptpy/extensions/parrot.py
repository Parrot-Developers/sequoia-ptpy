'''This module extends PTP for Parrot devices.

Use it in a master module that determines the vendor and automatically uses its
extension.
'''
from construct import (
    Container, Enum, ExprAdapter, Pass, Struct,
)
import logging
logger = logging.getLogger(__name__)

__all__ = ('Parrot',)


class Parrot(object):
    '''This class implements Parrot's PTP operations.'''

    def __init__(self, *args, **kwargs):
        logger.debug('Init Parrot')
        super(Parrot, self).__init__(*args, **kwargs)

    def _PropertyCode(self, **product_properties):
        return super(Parrot, self)._PropertyCode(
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
            LEDsEnableMask=0xD220,
            GPSEnable=0xD221,
            SelectedStorage=0xD222,
            MediaFolderName=0xD223,
            XMPTag=0xD224,
            **product_properties
        )

    def _OperationCode(self, **product_operations):
        return super(Parrot, self)._OperationCode(
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
            SetGeotag=0x9400,
            **product_operations
        )

    def _ResponseCode(self, **product_responses):
        return super(Parrot, self)._ResponseCode(
            **product_responses
        )

    def _EventCode(self, **product_events):
        return super(Parrot, self)._EventCode(
            Status=0xC201,
            MagnetoCalibrationStatus=0xC202,
            **product_events
        )

    def _FilesystemType(self, **product_filesystem_types):
        return super(Parrot, self)._FilesystemType(
            **product_filesystem_types
        )

    def _Sunshine(self):
        return ExprAdapter(
            self._PTPArray(self._UInt32),
            encoder=lambda obj, ctx: [
                obj.Green[0], obj.Red[0], obj.RedEdge[0], obj.NIR[0],
                obj.Green[1], obj.Red[1], obj.RedEdge[1], obj.NIR[1],
            ],
            decoder=lambda obj, ctx: Container(
                Green=(obj[0], obj[4]),
                Red=(obj[1], obj[5]),
                RedEdge=(obj[2], obj[6]),
                NIR=(obj[3], obj[7]),
            ),
        )

    def _Temperature(self):
        return ExprAdapter(
            self._PTPArray(self._Int32),
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
            self._PTPArray(self._UInt32),
            encoder=lambda obj, ctx: [obj.Yaw, obj.Pitch, obj.Roll],
            decoder=lambda obj, ctx: Container(
                Yaw=obj[0], Pitch=obj[1], Roll=obj[2]
            ),
        )

    def _GPS(self):
        return ExprAdapter(
            self._PTPArray(self._UInt32),
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
            self._PTPArray(self._UInt32),
            encoder=lambda obj, ctx: [obj.X, obj.Y, obj.Z],
            decoder=lambda obj, ctx: Container(
                X=obj[0], Y=obj[1], Z=obj[2],
            ),
        )

    def _Accelerometer(self):
        return ExprAdapter(
            self._PTPArray(self._UInt32),
            encoder=lambda obj, ctx: [obj.X, obj.Y, obj.Z],
            decoder=lambda obj, ctx: Container(
                X=obj[0], Y=obj[1], Z=obj[2],
            ),
        )

    def _Magnetometer(self):
        return ExprAdapter(
            self._PTPArray(self._UInt32),
            encoder=lambda obj, ctx: [obj.X, obj.Y, obj.Z],
            decoder=lambda obj, ctx: Container(
                X=obj[0], Y=obj[1], Z=obj[2],
            ),
        )

    def _IMU(self):
        return ExprAdapter(
            self._PTPArray(self._UInt32),
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
        # Status flags from LSB to MSB
        status = [
            'SnapshotRequested',
            'BodyImuCalibRunning',
            'AuxiliaryImuCalibRunning',
            'AuxiliaryConnected',
            'AuxiliaryGpsRunning',
            'RemoteGpsRunning',
            'CamRGBError',
            'CamGreenError',
            'CamRedError',
            'CamRedEdgeError',
            'CamNIRError',
            'BodySensorsInitDone',
            'AuxiliarySensorsInitDone',
            'CameraRunning',
        ]
        return ExprAdapter(
            self._UInt32,
            encoder=lambda obj, ctx: sum(
                [
                    0x1 << i if getattr(obj, n, False) else 0
                    for i, n in enumerate(status)
                ]
            ),
            decoder=lambda obj, ctx: Container(
                {n: (obj & (0x01 << i)) != 0 for i, n in enumerate(status)}
            ),
        )

    def _LEDsEnable(self):
        # Status flags from LSB to MSB
        leds = [
            'Body',
            'Auxiliary',
        ]
        return ExprAdapter(
            self._UInt32,
            encoder=lambda obj, ctx: sum(
                [
                    0x1 << i if getattr(obj, n, False) else 0
                    for i, n in enumerate(leds)
                ]
            ),
            decoder=lambda obj, ctx: Container(
                {n: (obj & (0x01 << i)) != 0 for i, n in enumerate(leds)}
            ),
        )

    def _MagnetoStatus(self):
        return Enum(
            self._UInt32,
            default=Pass,
            CalibrationOk=1,
            CalibrationRunning=2,
            CalibrationRollPending=3,
            CalibrationPitchPending=4,
            CalibrationYawPending=5,
            CalibrationFailed=6,
            CalibrationAborted=7,
        )

    def _Geotag(self):
        return ExprAdapter(
            Struct(
                'ValidityMask' / self._UInt32,
                'Timestamp' / self._Int64,
                'Latitude' / self._Int32,
                'Longitude' / self._Int32,
                'Altitude' / self._Int32,
                'Satellites' / self._UInt32,
                'AccuracyXY' / self._UInt32,
                'AccuracyZ' / self._UInt32,
                'NorthSpeed' / self._Int32,
                'EastSpeed' / self._Int32,
                'UpSpeed' / self._Int32,
                'Roll' / self._Int32,
                'Pitch' / self._Int32,
                'Yaw' / self._Int32,
            ),
            encoder=lambda obj, ctx:
            Container(
                ValidityMask=obj.ValidityMask,
                Timestamp=obj.Timestamp,
                Latitude=int(obj.Latitude * 10**7),
                Longitude=int(obj.Longitude * 10**7),
                Altitude=int(obj.Altitude * 1000),
                Satellites=obj.Satellites,
                AccuracyXY=int(obj.AccuracyXY * 1000),
                AccuracyZ=int(obj.AccuracyZ * 1000),
                NorthSpeed=int(obj.NorthSpeed * 1000),
                EastSpeed=int(obj.EastSpeed * 1000),
                UpSpeed=int(obj.UpSpeed * 1000),
                Roll=int(obj.Roll * 1000),
                Pitch=int(obj.Pitch * 1000),
                Yaw=int(obj.Yaw * 1000),
            ),
            decoder=lambda obj, ctx: Container(
                obj.ValidityMask,
                obj.Timestamp,
                obj.Latitude / 10.**7.,
                obj.Longitude / 10.**7.,
                obj.Altitude / 1000.,
                obj.Satellites,
                obj.AccuracyXY / 1000.,
                obj.AccuracyZ / 1000.,
                obj.NorthSpeed / 1000.,
                obj.EastSpeed / 1000.,
                obj.UpSpeed / 1000.,
                obj.Roll / 1000.,
                obj.Pitch / 1000.,
                obj.Yaw / 1000.,
            ),
        )

    def _set_endian(self, endian):
        super(Parrot, self)._set_endian(endian)
        logger.debug('Set Parrot endianness')
        self._Sunshine = self._Sunshine()
        self._Temperature = self._Temperature()
        self._Angle = self._Angle()
        self._GPS = self._GPS()
        self._Gyroscope = self._Gyroscope()
        self._Accelerometer = self._Accelerometer()
        self._Magnetometer = self._Magnetometer()
        self._IMU = self._IMU()
        self._Status = self._Status()
        self._LEDsEnable = self._LEDsEnable()
        self._MagnetoStatus = self._MagnetoStatus()
        self._Geotag = self._Geotag()

    def get_sunshine_values(self):
        ptp = Container(
            OperationCode='GetSunshineValues',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._Sunshine)

    def get_temperature_values(self):
        ptp = Container(
            OperationCode='GetTemperatureValues',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._Temperature)

    def get_angle_values(self, imu_id=0):
        ptp = Container(
            OperationCode='GetAngleValues',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._Angle)

    def get_gps_values(self):
        ptp = Container(
            OperationCode='GetGpsValues',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._GPS)

    def get_gyroscope_values(self, imu_id=0):
        ptp = Container(
            OperationCode='GetGyroscopeValues',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._Gyroscope)

    def get_accelerometer_values(self, imu_id=0):
        ptp = Container(
            OperationCode='GetAccelerometerValues',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._Accelerometer)

    def get_magnetometer_values(self, imu_id=0):
        ptp = Container(
            OperationCode='GetMagnetometerValues',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._Magnetometer)

    def get_imu_values(self, imu_id=0):
        ptp = Container(
            OperationCode='GetImuValues',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._IMU)

    def get_status_mask(self, imu_id=0):
        ptp = Container(
            OperationCode='GetStatusMask',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._Status)

    def eject_storage(self, storage_id):
        ptp = Container(
            OperationCode='EjectStorage',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[storage_id]
        )
        return self.mesg(ptp)

    def start_magneto_calib(self, imu_id=0):
        ptp = Container(
            OperationCode='StartMagnetoCalib',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[imu_id]
        )
        return self.mesg(ptp)

    def stop_magneto_calib(self, imu_id=0):
        ptp = Container(
            OperationCode='StopMagnetoCalib',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[imu_id]
        )
        return self.mesg(ptp)

    def get_magneto_calib_status(self, imu_id=0):
        ptp = Container(
            OperationCode='MagnetoCalibStatus',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[imu_id]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._MagnetoStatus)

    def send_firmware(self, firmware):
        '''Send PLF for update'''
        ptp = Container(
            OperationCode='SendFirmwareUpdate',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[len(firmware)]
        )
        return self.send(ptp, firmware)

    def set_geotag(self, geotag):
        geotag = self._build_if_not_data(geotag, self._Geotag)
        ptp = Container(
            OperationCode='SetGeotag',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        return self.send(ptp, geotag)
