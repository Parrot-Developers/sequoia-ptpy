'''This module extends PTPDevice for Canon devices.

Use it in a master module that determines the vendor and automatically uses its
extension. This is why inheritance is not explicit.
'''
from ...util import _main_thread_alive
from .properties import EOSPropertiesMixin
from contextlib import contextmanager
from construct import (
    Array, Byte, Container, Embedded, Enum, Pass, PrefixedArray, Range, Struct,
    Switch, Computed
)
from six.moves.queue import Queue
from threading import Thread, Event
from time import sleep
import atexit
import logging
logger = logging.getLogger(__name__)

__all__ = ('Canon',)


class Canon(EOSPropertiesMixin, object):
    '''This class implements Canon's PTP operations.'''
    def __init__(self, *args, **kwargs):
        logger.debug('Init Canon')
        super(Canon, self).__init__(*args, **kwargs)
        # TODO: expose the choice to poll or not Canon events
        self.__no_polling = False
        self.__eos_event_shutdown = Event()
        self.__eos_event_proc = None

    @contextmanager
    def session(self):
        '''
        Manage Canon session with context manager.
        '''
        # When raw device, do not perform
        if self.__no_polling:
            with super(Canon, self).session():
                yield
            return
        # Within a normal PTP session
        with super(Canon, self).session():
            # Set up remote mode and extended event info
            self.eos_set_remote_mode(1)
            self.eos_event_mode(1)
            # And launch a polling thread
            self.__event_queue = Queue()
            self.__eos_event_proc = Thread(
                name='EOSEvtPolling',
                target=self.__eos_poll_events
            )
            self.__eos_event_proc.daemon = False
            atexit.register(self._eos_shutdown)
            self.__eos_event_proc.start()

            try:
                yield
            finally:
                self._eos_shutdown()

    def _shutdown(self):
        self._eos_shutdown()
        super(Canon, self)._shutdown()

    def _eos_shutdown(self):
        logger.debug('Shutdown EOS events request')
        self.__eos_event_shutdown.set()

        # Only join a running thread.
        if self.__eos_event_proc and self.__eos_event_proc.is_alive():
            self.__eos_event_proc.join(2)

    def _PropertyCode(self, **product_properties):
        return super(Canon, self)._PropertyCode(
            BeepMode=0xD001,
            ViewfinderMode=0xD003,
            ImageQuality=0xD006,
            CanonImageSize=0xD008,
            CanonFlashMode=0xD00A,
            TvAvSetting=0xD00C,
            MeteringMode=0xD010,
            MacroMode=0xD011,
            FocusingPoint=0xD012,
            CanonWhiteBalance=0xD013,
            ISOSpeed=0xD01C,
            Aperture=0xD01D,
            ShutterSpeed=0xD01E,
            ExpCompensation=0xD01F,
            Zoom=0xD02A,
            SizeQualityMode=0xD02C,
            FlashMemory=0xD031,
            CameraModel=0xD032,
            CameraOwner=0xD033,
            UnixTime=0xD034,
            ViewfinderOutput=0xD036,
            RealImageWidth=0xD039,
            PhotoEffect=0xD040,
            AssistLight=0xD041,
            **product_properties
        )

    def _OperationCode(self, **product_operations):
        return super(Canon, self)._OperationCode(
            GetObjectSize=0x9001,
            SetObjectArchive=0x9002,
            KeepDeviceOn=0x9003,
            LockDeviceUI=0x9004,
            UnlockDeviceUI=0x9005,
            GetObjectHandleByName=0x9006,
            InitiateReleaseControl=0x9008,
            TerminateReleaseControl=0x9009,
            TerminatePlaybackMode=0x900A,
            ViewfinderOn=0x900B,
            ViewfinderOff=0x900C,
            DoAeAfAwb=0x900D,
            GetCustomizeSpec=0x900E,
            GetCustomizeItemInfo=0x900F,
            GetCustomizeData=0x9010,
            SetCustomizeData=0x9011,
            GetCaptureStatus=0x9012,
            CheckEvent=0x9013,
            FocusLock=0x9014,
            FocusUnlock=0x9015,
            GetLocalReleaseParam=0x9016,
            SetLocalReleaseParam=0x9017,
            AskAboutPcEvf=0x9018,
            SendPartialObject=0x9019,
            InitiateCaptureInMemory=0x901A,
            GetPartialObjectEx=0x901B,
            SetObjectTime=0x901C,
            GetViewfinderImage=0x901D,
            GetObjectAttributes=0x901E,
            ChangeUSBProtocol=0x901F,
            GetChanges=0x9020,
            GetObjectInfoEx=0x9021,
            InitiateDirectTransfer=0x9022,
            TerminateDirectTransfer=0x9023,
            SendObjectInfoByPath=0x9024,
            SendObjectByPath=0x9025,
            InitiateDirectTansferEx=0x9026,
            GetAncillaryObjectHandles=0x9027,
            GetTreeInfo=0x9028,
            GetTreeSize=0x9029,
            NotifyProgress=0x902A,
            NotifyCancelAccepted=0x902B,
            GetDirectory=0x902D,
            SetPairingInfo=0x9030,
            GetPairingInfo=0x9031,
            DeletePairingInfo=0x9032,
            GetMACAddress=0x9033,
            SetDisplayMonitor=0x9034,
            PairingComplete=0x9035,
            GetWirelessMAXChannel=0x9036,
            EOSGetStorageIDs=0x9101,
            EOSGetStorageInfo=0x9102,
            EOSGetObjectInfo=0x9103,
            EOSGetObject=0x9104,
            EOSDeleteObject=0x9105,
            EOSFormatStore=0x9106,
            EOSGetPartialObject=0x9107,
            EOSGetDeviceInfoEx=0x9108,
            EOSGetObjectInfoEx=0x9109,
            EOSGetThumbEx=0x910A,
            EOSSendPartialObject=0x910B,
            EOSSetObjectAttributes=0x910C,
            EOSGetObjectTime=0x910D,
            EOSSetObjectTime=0x910E,
            EOSRemoteRelease=0x910F,
            EOSSetDevicePropValueEx=0x9110,
            EOSGetRemoteMode=0x9113,
            EOSSetRemoteMode=0x9114,
            EOSSetEventMode=0x9115,
            EOSGetEvent=0x9116,
            EOSTransferComplete=0x9117,
            EOSCancelTransfer=0x9118,
            EOSResetTransfer=0x9119,
            EOSPCHDDCapacity=0x911A,
            EOSSetUILock=0x911B,
            EOSResetUILock=0x911C,
            EOSKeepDeviceOn=0x911D,
            EOSSetNullPacketMode=0x911E,
            EOSUpdateFirmware=0x911F,
            EOSTransferCompleteDT=0x9120,
            EOSCancelTransferDT=0x9121,
            EOSSetWftProfile=0x9122,
            EOSGetWftProfile=0x9122,
            EOSSetProfileToWft=0x9124,
            EOSBulbStart=0x9125,
            EOSBulbEnd=0x9126,
            EOSRequestDevicePropValue=0x9127,
            EOSRemoteReleaseOn=0x9128,
            EOSRemoteReleaseOff=0x9129,
            EOSInitiateViewfinder=0x9151,
            EOSTerminateViewfinder=0x9152,
            EOSGetViewFinderImage=0x9153,
            EOSDoAf=0x9154,
            EOSDriveLens=0x9155,
            EOSDepthOfFieldPreview=0x9156,
            EOSClickWB=0x9157,
            EOSZoom=0x9158,
            EOSZoomPosition=0x9159,
            EOSSetLiveAfFrame=0x915a,
            EOSAfCancel=0x9160,
            EOSFAPIMessageTX=0x91FE,
            EOSFAPIMessageRX=0x91FF,
            **product_operations
        )

    def _ObjectFormatCode(self, **product_object_formats):
        return super(Canon, self)._ObjectFormatCode(
            CRW=0xB101,
            CRW3=0xB103,
            MOV=0xB104,
            **product_object_formats
        )

    def _ResponseCode(self, **product_responses):
        return super(Canon, self)._ResponseCode(
            **product_responses
        )

    def _EventCode(self, **product_events):
        return super(Canon, self)._EventCode(
            CanonDeviceInfoChanged=0xC008,
            CanonRequestObjectTransfer=0xC009,
            CameraModeChanged=0xC00C,
            **product_events
        )

    def _FilesystemType(self, **product_filesystem_types):
        return super(Canon, self)._FilesystemType(
            **product_filesystem_types
        )

    def _EOSEventCode(self):
        '''Return desired endianness for Canon EOS event codes'''
        return Enum(
            self._UInt32,
            default=Pass,
            EmptyEvent=0x0000,
            RequestGetEvent=0xC101,
            ObjectAdded=0xC181,
            ObjectRemoved=0xC182,
            RequestGetObjectInfoEx=0xC183,
            StorageStatusChanged=0xC184,
            StorageInfoChanged=0xC185,
            RequestObjectTransfer=0xC186,
            ObjectInfoChangedEx=0xC187,
            ObjectContentChanged=0xC188,
            DevicePropChanged=0xC189,
            AvailListChanged=0xC18A,
            CameraStatusChanged=0xC18B,
            WillSoonShutdown=0xC18D,
            ShutdownTimerUpdated=0xC18E,
            RequestCancelTransfer=0xC18F,
            RequestObjectTransferDT=0xC190,
            RequestCancelTransferDT=0xC191,
            StoreAdded=0xC192,
            StoreRemoved=0xC193,
            BulbExposureTime=0xC194,
            RecordingTime=0xC195,
            InnerDevelopParam=0xC196,
            RequestObjectTransferDevelop=0xC197,
            GPSLogOutputProgress=0xC198,
            GPSLogOutputComplete=0xC199,
            TouchTrans=0xC19A,
            RequestObjectTransferExInfo=0xC19B,
            PowerZoomInfoChanged=0xC19D,
            RequestPushMode=0xC19F,
            RequestObjectTransferTS=0xC1A2,
            AfResult=0xC1A3,
            CTGInfoCheckComplete=0xC1A4,
            OLCInfoChanged=0xC1A5,
            ObjectAddedEx64=0xC1A7,
            ObjectInfoChangedEx64=0xC1A8,
            RequestObjectTransfer64=0xC1A9,
            RequestObjectTransferFTP64=0xC1AB,
            ImportFailed=0xC1AF,
            BlePairing=0xC1B0,
            RequestObjectTransferFTP=0xC1F1,
            UnknownError=0xFFFFFFFF,
        )

    def _EOSPropertyCode(self):
        '''Return desired endianness for Canon EOS property codes'''
        return Enum(
            self._UInt32,
            default=Pass,
            Aperture=0xD101,
            ShutterSpeed=0xD102,
            ISO=0xD103,
            ExposureCompensation=0xD104,
            ShootingMode=0xD105,
            DriveMode=0xD106,
            ExposureMeteringMode=0xD107,
            AutoFocusMode=0xD108,
            WhiteBalance=0xD109,
            ColorTemperature=0xD10A,
            WhiteBalanceAdjustBA=0xD10B,
            WhiteBalanceAdjustMG=0xD10C,
            WhiteBalanceBracketBA=0xD10D,
            WhiteBalanceBracketMG=0xD10E,
            ColorSpace=0xD10F,
            PictureStyle=0xD110,
            BatteryPower=0xD111,
            BatterySelect=0xD112,
            CameraTime=0xD113,
            AutoPowerOff=0xD114,
            Owner=0xD115,
            ModelID=0xD116,
            PTPExtensionVersion=0xD119,
            DPOFVersion=0xD11A,
            AvailableShots=0xD11B,
            CaptureDestination=0xD11C,
            BracketMode=0xD11D,
            CurrentStorage=0xD11E,
            CurrentFolder=0xD11F,
            ImageFormat=0xD120,
            ImageFormatCF=0xD121,
            ImageFormatSD=0xD122,
            ImageFormatHDD=0xD123,
            CompressionS=0xD130,
            CompressionM1=0xD131,
            CompressionM2=0xD132,
            CompressionL=0xD133,
            AEModeDial=0xD138,
            AEModeCustom=0xD139,
            MirrorUpSetting=0xD13A,
            HighlightTonePriority=0xD13B,
            AFSelectFocusArea=0xD13C,
            HDRSetting=0xD13D,
            PCWhiteBalance1=0xD140,
            PCWhiteBalance2=0xD141,
            PCWhiteBalance3=0xD142,
            PCWhiteBalance4=0xD143,
            PCWhiteBalance5=0xD144,
            MWhiteBalance=0xD145,
            MWhiteBalanceEx=0xD146,
            PictureStyleStandard=0xD150,
            PictureStylePortrait=0xD151,
            PictureStyleLandscape=0xD152,
            PictureStyleNeutral=0xD153,
            PictureStyleFaithful=0xD154,
            PictureStyleBlackWhite=0xD155,
            PictureStyleAuto=0xD156,
            PictureStyleUserSet1=0xD160,
            PictureStyleUserSet2=0xD161,
            PictureStyleUserSet3=0xD162,
            PictureStyleParam1=0xD170,
            PictureStyleParam2=0xD171,
            PictureStyleParam3=0xD172,
            HighISOSettingNoiseReduction=0xD178,
            MovieServoAF=0xD179,
            ContinuousAFValid=0xD17A,
            Attenuator=0xD17B,
            UTCTime=0xD17C,
            Timezone=0xD17D,
            Summertime=0xD17E,
            FlavorLUTParams=0xD17F,
            CustomFunc1=0xD180,
            CustomFunc2=0xD181,
            CustomFunc3=0xD182,
            CustomFunc4=0xD183,
            CustomFunc5=0xD184,
            CustomFunc6=0xD185,
            CustomFunc7=0xD186,
            CustomFunc8=0xD187,
            CustomFunc9=0xD188,
            CustomFunc10=0xD189,
            CustomFunc11=0xD18A,
            CustomFunc12=0xD18B,
            CustomFunc13=0xD18C,
            CustomFunc14=0xD18D,
            CustomFunc15=0xD18E,
            CustomFunc16=0xD18F,
            CustomFunc17=0xD190,
            CustomFunc18=0xD191,
            CustomFunc19=0xD192,
            InnerDevelop=0xD193,
            MultiAspect=0xD194,
            MovieSoundRecord=0xD195,
            MovieRecordVolume=0xD196,
            WindCut=0xD197,
            ExtenderType=0xD198,
            OLCInfoVersion=0xD199,
            CustomFuncEx=0xD1A0,
            MyMenu=0xD1A1,
            MyMenuList=0xD1A2,
            WftStatus=0xD1A3,
            WftInputTransmission=0xD1A4,
            HDDDirectoryStructure=0xD1A5,
            BatteryInfo=0xD1A6,
            AdapterInfo=0xD1A7,
            LensStatus=0xD1A8,
            QuickReviewTime=0xD1A9,
            CardExtension=0xD1AA,
            TempStatus=0xD1AB,
            ShutterCounter=0xD1AC,
            SpecialOption=0xD1AD,
            PhotoStudioMode=0xD1AE,
            SerialNumber=0xD1AF,
            EVFOutputDevice=0xD1B0,
            EVFMode=0xD1B1,
            DepthOfFieldPreview=0xD1B2,
            EVFSharpness=0xD1B3,
            EVFWBMode=0xD1B4,
            EVFClickWBCoeffs=0xD1B5,
            EVFColorTemp=0xD1B6,
            ExposureSimMode=0xD1B7,
            EVFRecordStatus=0xD1B8,
            LvAfSystem=0xD1BA,
            MovSize=0xD1BB,
            LvViewTypeSelect=0xD1BC,
            MirrorDownStatus=0xD1BD,
            MovieParam=0xD1BE,
            MirrorLockupState=0xD1BF,
            FlashChargingState=0xD1C0,
            AloMode=0xD1C1,
            FixedMovie=0xD1C2,
            OneShotRawOn=0xD1C3,
            ErrorForDisplay=0xD1C4,
            AEModeMovie=0xD1C5,
            BuiltinStroboMode=0xD1C6,
            StroboDispState=0xD1C7,
            StroboETTL2Metering=0xD1C8,
            ContinousAFMode=0xD1C9,
            MovieParam2=0xD1CA,
            StroboSettingExpComposition=0xD1CB,
            MovieParam3=0xD1CC,
            LVMedicalRotate=0xD1CF,
            Artist=0xD1D0,
            Copyright=0xD1D1,
            BracketValue=0xD1D2,
            FocusInfoEx=0xD1D3,
            DepthOfField=0xD1D4,
            Brightness=0xD1D5,
            LensAdjustParams=0xD1D6,
            EFComp=0xD1D7,
            LensName=0xD1D8,
            AEB=0xD1D9,
            StroboSetting=0xD1DA,
            StroboWirelessSetting=0xD1DB,
            StroboFiring=0xD1DC,
            LensID=0xD1DD,
            LCDBrightness=0xD1DE,
            CADarkBright=0xD1DF,
        )

    def _EOSEventRecords(self):
        '''Return desired endianness for EOS Event Records constructor'''
        return Range(
            # The dataphase can be about as long as a 32 bit unsigned int.
            0, 0xFFFFFFFF,
            self._EOSEventRecord
        )

    def _EOSEventRecord(self):
        '''Return desired endianness for a single EOS Event Record'''
        return Struct(
            'Bytes' / self._UInt32,
            Embedded(Struct(
                'EventCode' / self._EOSEventCode,
                'Record' / Switch(
                    lambda ctx: ctx.EventCode,
                    {
                        'AvailListChanged':
                        Embedded(Struct(
                            'PropertyCode' / self._EOSPropertyCode,
                            'Enumeration' / Array(
                                # TODO: Verify if this is actually an
                                # enumeration.
                                lambda ctx: ctx._._.Bytes - 12,
                                self._UInt8
                            )
                        )),
                        'DevicePropChanged':
                        Embedded(Struct(
                            'PropertyCode' / self._EOSPropertyCode,
                            'DataTypeCode' / Computed(
                                lambda ctx: self._EOSDataTypeCode[ctx.PropertyCode]
                            ),
                            'Value' / Switch(
                                lambda ctx: ctx.DataTypeCode,
                                {
                                    None: Array(
                                        lambda ctx: ctx._._.Bytes - 12,
                                        self._UInt8
                                    )
                                },
                                default=self._DataType
                            ),
                        )),
                        # TODO: 'EmptyEvent',
                        # TODO: 'RequestGetEvent',
                        # TODO: 'ObjectAdded',
                        # TODO: 'ObjectRemoved',
                        # TODO: 'RequestGetObjectInfoEx',
                        # TODO: 'StorageStatusChanged',
                        # TODO: 'StorageInfoChanged',
                        # TODO: 'RequestObjectTransfer',
                        # TODO: 'ObjectInfoChangedEx',
                        # TODO: 'ObjectContentChanged',
                        # TODO: 'DevicePropChanged',
                        # TODO: 'AvailListChanged',
                        # TODO: 'CameraStatusChanged',
                        # TODO: 'WillSoonShutdown',
                        # TODO: 'ShutdownTimerUpdated',
                        # TODO: 'RequestCancelTransfer',
                        # TODO: 'RequestObjectTransferDT',
                        # TODO: 'RequestCancelTransferDT',
                        # TODO: 'StoreAdded',
                        # TODO: 'StoreRemoved',
                        # TODO: 'BulbExposureTime',
                        # TODO: 'RecordingTime',
                        # TODO: 'InnerDevelopParam',
                        # TODO: 'RequestObjectTransferDevelop',
                        # TODO: 'GPSLogOutputProgress',
                        # TODO: 'GPSLogOutputComplete',
                        # TODO: 'TouchTrans',
                        # TODO: 'RequestObjectTransferExInfo',
                        # TODO: 'PowerZoomInfoChanged',
                        # TODO: 'RequestPushMode',
                        # TODO: 'RequestObjectTransferTS',
                        # TODO: 'AfResult',
                        # TODO: 'CTGInfoCheckComplete',
                        # TODO: 'OLCInfoChanged',
                        # TODO: 'ObjectAddedEx64',
                        # TODO: 'ObjectInfoChangedEx64',
                        # TODO: 'RequestObjectTransfer64',
                        # TODO: 'RequestObjectTransferFTP64',
                        # TODO: 'ImportFailed',
                        # TODO: 'BlePairing',
                        # TODO: 'RequestObjectTransferFTP',
                        # TODO: 'Unknown',
                    },
                    default=Array(
                        lambda ctx: ctx._.Bytes - 8,
                        self._UInt8
                    )
                )
            ))
        )

    def _EOSDeviceInfo(self):
        return Struct(
            'EventsSupported' / PrefixedArray(
                self._UInt32,
                self._EOSEventCode
            ),
            'DevicePropertiesSupported' / PrefixedArray(
                self._UInt32,
                self._EOSPropertyCode
            ),
            'TODO' / PrefixedArray(
                self._UInt32,
                self._UInt32
            ),
        )

    # TODO: Decode Canon specific events and properties.
    def _set_endian(self, endian):
        logger.debug('Set Canon endianness')
        # HACK: The DataType mechanism used for automatic parsing introduces
        # HACK: some nasty dependencies, so the PTP types need to be declared
        # HACK: before the extension types, and then finally the DataType at
        # HACK: the end...
        # TODO: This could probably use a decorator to automatically work out the
        # TODO: right order...
        super(Canon, self)._set_endian(endian, explicit=True)

        # Prepare these for DataType
        self._EOSPropertyCode = self._EOSPropertyCode()
        self._EOSEventCode = self._EOSEventCode()
        self._EOSImageSize = self._EOSImageSize()
        self._EOSImageType = self._EOSImageType()
        self._EOSImageCompression = self._EOSImageCompression()
        self._EOSImageFormat = self._EOSImageFormat()
        self._EOSWhiteBalance = self._EOSWhiteBalance()
        self._EOSFocusMode = self._EOSFocusMode()

        # Make sure DataType is available
        super(Canon, self)._set_endian(endian, explicit=False)

        # Use DataType
        self._EOSEventRecord = self._EOSEventRecord()
        self._EOSEventRecords = self._EOSEventRecords()


    # TODO: implement GetObjectSize
    # TODO: implement SetObjectArchive

    def keep_device_on(self):
        '''Ping non EOS camera so it stays ON'''
        ptp = Container(
            OperationCode='KeepDeviceOn',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.mesg(ptp)
        return response

    # TODO: implement LockDeviceUI
    # TODO: implement UnlockDeviceUI
    # TODO: implement GetObjectHandleByName
    # TODO: implement InitiateReleaseControl
    # TODO: implement TerminateReleaseControl
    # TODO: implement TerminatePlaybackMode
    # TODO: implement ViewfinderOn
    # TODO: implement ViewfinderOff
    # TODO: implement DoAeAfAwb
    # TODO: implement GetCustomizeSpec
    # TODO: implement GetCustomizeItemInfo
    # TODO: implement GetCustomizeData
    # TODO: implement SetCustomizeData
    # TODO: implement GetCaptureStatus
    # TODO: implement CheckEvent
    # TODO: implement FocusLock
    # TODO: implement FocusUnlock
    # TODO: implement GetLocalReleaseParam
    # TODO: implement SetLocalReleaseParam
    # TODO: implement AskAboutPcEvf
    # TODO: implement SendPartialObject
    # TODO: implement InitiateCaptureInMemory
    # TODO: implement GetPartialObjectEx
    # TODO: implement SetObjectTime
    # TODO: implement GetViewfinderImage
    # TODO: implement GetObjectAttributes
    # TODO: implement ChangeUSBProtocol
    # TODO: implement GetChanges
    # TODO: implement GetObjectInfoEx
    # TODO: implement InitiateDirectTransfer
    # TODO: implement TerminateDirectTransfer
    # TODO: implement SendObjectInfoByPath
    # TODO: implement SendObjectByPath
    # TODO: implement InitiateDirectTansferEx
    # TODO: implement GetAncillaryObjectHandles
    # TODO: implement GetTreeInfo
    # TODO: implement GetTreeSize
    # TODO: implement NotifyProgress
    # TODO: implement NotifyCancelAccepted
    # TODO: implement GetDirectory
    # TODO: implement SetPairingInfo
    # TODO: implement GetPairingInfo
    # TODO: implement DeletePairingInfo
    # TODO: implement GetMACAddress
    # TODO: implement SetDisplayMonitor
    # TODO: implement PairingComplete
    # TODO: implement GetWirelessMAXChannel
    # TODO: implement EOSGetStorageIDs
    # TODO: implement EOSGetStorageInfo
    # TODO: implement EOSGetObjectInfo
    # TODO: implement EOSGetObject
    # TODO: implement EOSDeleteObject
    # TODO: implement EOSFormatStore
    # TODO: implement EOSGetPartialObject
    # TODO: implement EOSGetDeviceInfoEx

    def eos_get_device_info(self):
        '''Get EOS camera device information'''
        ptp = Container(
            OperationCode='EOSGetDeviceInfoEx',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[0x00100000]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._EOSDeviceInfo)

    # TODO: implement EOSGetObjectInfoEx
    # TODO: implement EOSGetThumbEx
    # TODO: implement EOSSendPartialObject
    # TODO: implement EOSSetObjectAttributes
    # TODO: implement EOSGetObjectTime
    # TODO: implement EOSSetObjectTime

    def eos_remote_release(self):
        '''Release shutter remotely on EOS cameras'''
        ptp = Container(
            OperationCode='EOSRemoteRelease',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.mesg(ptp)
        return response

    # TODO: implement EOSSetDevicePropValueEx
    # TODO: implement EOSGetRemoteMode

    def eos_set_remote_mode(self, mode):
        '''Set remote mode on EOS cameras'''

        # TODO: Add automatic translation of remote mode codes and names.
        code = mode
        ptp = Container(
            OperationCode='EOSSetRemoteMode',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[code]
        )
        response = self.mesg(ptp)
        return response

    def eos_event_mode(self, mode):
        '''Set event mode on EOS cameras'''
        # Canon extension uses this to enrich the events returned by the camera
        # as well as allowing for polling at the convenience of the initiator.

        # TODO: Add automatic translation of event mode codes and names.
        code = mode
        ptp = Container(
            OperationCode='EOSSetEventMode',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[code]
        )
        response = self.mesg(ptp)
        return response

    def eos_get_event(self):
        '''Poll EOS camera for EOS events'''
        ptp = Container(
            OperationCode='EOSGetEvent',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._EOSEventRecords)

    def eos_transfer_complete(self, handle):
        '''Terminate a transfer for EOS Cameras'''
        ptp = Container(
            OperationCode='EOSTransferComplete',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[handle]
        )
        response = self.mesg(ptp)
        return response

    # TODO: implement EOSCancelTransfer
    # TODO: implement EOSResetTransfer

    def eos_pc_hdd_capacity(self, todo0=0xfffffff8, todo1=0x1000, todo2=0x1):
        '''Tell EOS camera about PC hard drive capacity'''
        # TODO: Figure out what to send exactly.
        ptp = Container(
            OperationCode='EOSPCHDDCapacity',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[todo0, todo1, todo2]
        )
        response = self.mesg(ptp)
        return response

    def eos_set_ui_lock(self):
        '''Lock user interface on EOS cameras'''
        ptp = Container(
            OperationCode='EOSSetUILock',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.mesg(ptp)
        return response

    def eos_reset_ui_lock(self):
        '''Unlock user interface on EOS cameras'''
        ptp = Container(
            OperationCode='EOSResetUILock',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.mesg(ptp)
        return response

    def eos_keep_device_on(self):
        '''Ping EOS camera so it stays ON'''
        ptp = Container(
            OperationCode='EOSKeepDeviceOn',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.mesg(ptp)
        return response

    # TODO: implement EOSSetNullPacketMode
    # TODO: implement EOSUpdateFirmware
    # TODO: implement EOSTransferCompleteDT
    # TODO: implement EOSCancelTransferDT
    # TODO: implement EOSSetWftProfile
    # TODO: implement EOSGetWftProfile
    # TODO: implement EOSSetProfileToWft

    # TODO: implement method convenience method for bulb captures
    def eos_bulb_start(self):
        '''Begin bulb capture on EOS cameras'''
        ptp = Container(
            OperationCode='EOSBulbStart',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.mesg(ptp)
        return response

    def eos_bulb_end(self):
        '''End bulb capture on EOS cameras'''
        ptp = Container(
            OperationCode='EOSBulbEnd',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.mesg(ptp)
        return response

    def eos_request_device_prop_value(self, device_property):
        '''End bulb capture on EOS cameras'''
        ptp = Container(
            OperationCode='EOSRequestDevicePropValue',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[device_property]
        )
        response = self.mesg(ptp)
        return response

    def eos_remote_release_on(self, full=False, m=False, x=0):
        '''
        Remote control shutter press for EOS cameras

        This is the equivalent of pressing the shutter button: all the way in
        if `full` or half-way otherwise.

        For Canon EOS M, there is only full press with a special argument.
        '''
        ptp = Container(
            OperationCode='EOSRemoteReleaseOn',
            SessionID=self._session,
            TransactionID=self._transaction,
            # TODO: figure out what x means.
            Parameter=[0x3 if m else (0x2 if full else 0x1), x]
        )
        response = self.mesg(ptp)
        return response

    def eos_remote_release_off(self, full=False, m=False):
        '''
        Remote control shutter release for EOS cameras

        This is the equivalent of releasing the shutter button: from all the
        way in if `full` or from half-way otherwise.

        For Canon EOS M, there is only full press with a special argument.
        '''
        ptp = Container(
            OperationCode='EOSRemoteReleaseOff',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[0x3 if m else (0x2 if full else 0x1)]
        )
        response = self.mesg(ptp)
        return response

    # TODO: implement EOSInitiateViewfinder
    # TODO: implement EOSTerminateViewfinder
    # TODO: implement EOSGetViewFinderImage

    def eos_get_viewfinder_image(self):
        '''Get viefinder image for EOS cameras'''
        ptp = Container(
            OperationCode='EOSGetViewFinderImage',
            SessionID=self._session,
            TransactionID=self._transaction,
            # TODO: Find out what this parameter does.
            Parameter=[0x00100000]
        )
        return self.recv(ptp)

    def eos_do_af(self):
        '''Perform auto-focus with AF lenses set to AF'''

        ptp = Container(
            OperationCode='EOSDoAf',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.mesg(ptp)
        return response

    def eos_drive_lens(self, infinity=True, step=2):
        '''
        Drive lens focus on EOS cameras with an auto-focus lens on.

        `step` lies in the interval [-3, 3]. Its sign reverses the infinity
        argument. If `infinity` is `True`, the focal plane is driven away from
        the camera with the given step.

        The magnitude of `step` is qualitatively `1` for "fine", `2` for
        "normal" and `3` for "coarse".
        '''

        if step not in range(-3, 4):
            raise ValueError(
                'The step must be within [-3, 3].'
            )

        infinity = not infinity if step < 0 else infinity
        step = -step if step < 0 else step
        instruction = 0x8000 if infinity else 0x0000
        instruction |= step

        ptp = Container(
            OperationCode='EOSDriveLens',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[instruction]
        )
        response = self.mesg(ptp)
        return response

    # TODO: implement EOSDepthOfFieldPreview
    # TODO: implement EOSClickWB
    # TODO: implement EOSZoom
    # TODO: implement EOSZoomPosition
    # TODO: implement EOSSetLiveAfFrame

    def eos_af_cancel(self):
        '''Stop driving AF on EOS cameras.'''

        ptp = Container(
            OperationCode='EOSAfCancel',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.mesg(ptp)
        return response

    # TODO: implement EOSFAPIMessageTX
    # TODO: implement EOSFAPIMessageRX

    def event(self, wait=False):
        '''Check Canon or PTP events

        If `wait` this function is blocking. Otherwise it may return None.
        '''
        # TODO: Do something reasonable on wait=True
        evt = None
        timeout = None if wait else 0.001
        # TODO: Join queues to preserve order of Canon and PTP events.
        if not self.__event_queue.empty():
            evt = self.__event_queue.get(block=not wait, timeout=timeout)
        else:
            evt = super(Canon, self).event(wait=wait)

        return evt

    def __eos_poll_events(self):
        '''Poll events, adding them to a queue.'''
        while not self.__eos_event_shutdown.is_set() and _main_thread_alive():
            try:
                evts = self.eos_get_event()
                if evts:
                    for evt in evts:
                        logger.debug('Event queued')
                        logger.debug(evt)
                        self.__event_queue.put(evt)
            except Exception as e:
                logger.error(e)
            sleep(0.2)
        self.__eos_event_shutdown.clear()
