'''This module extends PTP for Nikon devices.
Use it in a master module that determines the vendor and automatically uses its
extension. This is why inheritance is not explicit.
'''
from ..util import _main_thread_alive
from construct import (
    Container, PrefixedArray, Struct,
)
from contextlib import contextmanager
from six.moves.queue import Queue
from threading import Thread, Event
from time import sleep
import atexit
import logging
logger = logging.getLogger(__name__)

__all__ = ('Nikon',)


class Nikon(object):
    '''This class implements Nikon's PTP operations.'''

    def __init__(self, *args, **kwargs):
        logger.debug('Init Nikon')
        super(Nikon, self).__init__(*args, **kwargs)
        # TODO: expose the choice to poll or not Nikon events
        self.__no_polling = False
        self.__nikon_event_shutdown = Event()
        self.__nikon_event_proc = None

    @contextmanager
    def session(self):
        '''
        Manage Nikon session with context manager.
        '''
        # When raw device, do not perform
        if self.__no_polling:
            with super(Nikon, self).session():
                yield
            return
        # Within a normal PTP session
        with super(Nikon, self).session():
            # launch a polling thread
            self.__event_queue = Queue()
            self.__nikon_event_proc = Thread(
                name='NikonEvtPolling',
                target=self.__nikon_poll_events
            )
            self.__nikon_event_proc.daemon = False
            atexit.register(self._nikon_shutdown)
            self.__nikon_event_proc.start()

            try:
                yield
            finally:
                self._nikon_shutdown()

    def _shutdown(self):
        self._nikon_shutdown()
        super(Nikon, self)._shutdown()

    def _nikon_shutdown(self):
        logger.debug('Shutdown Nikon events')
        self.__nikon_event_shutdown.set()

        # Only join a running thread.
        if self.__nikon_event_proc and self.__nikon_event_proc.is_alive():
            self.__nikon_event_proc.join(2)

    def _PropertyCode(self, **product_properties):
        props = {
            'ShootingBank': 0xD010,
            'ShootingBankNameA': 0xD011,
            'ShootingBankNameB': 0xD012,
            'ShootingBankNameC': 0xD013,
            'ShootingBankNameD': 0xD014,
            'ResetBank0': 0xD015,
            'RawCompression': 0xD016,
            'WhiteBalanceAutoBias': 0xD017,
            'WhiteBalanceTungstenBias': 0xD018,
            'WhiteBalanceFluorescentBias': 0xD019,
            'WhiteBalanceDaylightBias': 0xD01A,
            'WhiteBalanceFlashBias': 0xD01B,
            'WhiteBalanceCloudyBias': 0xD01C,
            'WhiteBalanceShadeBias': 0xD01D,
            'WhiteBalanceColorTemperature': 0xD01E,
            'WhiteBalancePresetNo': 0xD01F,
            'WhiteBalancePresetName0': 0xD020,
            'WhiteBalancePresetName1': 0xD021,
            'WhiteBalancePresetName2': 0xD022,
            'WhiteBalancePresetName3': 0xD023,
            'WhiteBalancePresetName4': 0xD024,
            'WhiteBalancePresetVal0': 0xD025,
            'WhiteBalancePresetVal1': 0xD026,
            'WhiteBalancePresetVal2': 0xD027,
            'WhiteBalancePresetVal3': 0xD028,
            'WhiteBalancePresetVal4': 0xD029,
            'ImageSharpening': 0xD02A,
            'ToneCompensation': 0xD02B,
            'ColorModel': 0xD02C,
            'HueAdjustment': 0xD02D,
            'NonCPULensDataFocalLength': 0xD02E,
            'NonCPULensDataMaximumAperture': 0xD02F,
            'ShootingMode': 0xD030,
            'JPEGCompressionPolicy': 0xD031,
            'ColorSpace': 0xD032,
            'AutoDXCrop': 0xD033,
            'FlickerReduction': 0xD034,
            'RemoteMode': 0xD035,
            'VideoMode': 0xD036,
            'NikonEffectMode': 0xD037,
            'Mode': 0xD038,
            'CSMMenuBankSelect': 0xD040,
            'MenuBankNameA': 0xD041,
            'MenuBankNameB': 0xD042,
            'MenuBankNameC': 0xD043,
            'MenuBankNameD': 0xD044,
            'ResetBank': 0xD045,
            'A1AFCModePriority': 0xD048,
            'A2AFSModePriority': 0xD049,
            'A3GroupDynamicAF': 0xD04A,
            'A4AFActivation': 0xD04B,
            'FocusAreaIllumManualFocus': 0xD04C,
            'FocusAreaIllumContinuous': 0xD04D,
            'FocusAreaIllumWhenSelected': 0xD04E,
            'FocusAreaWrap': 0xD04F,
            'VerticalAFON': 0xD050,
            'AFLockOn': 0xD051,
            'FocusAreaZone': 0xD052,
            'EnableCopyright': 0xD053,
            'ISOAuto': 0xD054,
            'EVISOStep': 0xD055,
            'EVStep': 0xD056,
            'EVStepExposureComp': 0xD057,
            'ExposureCompensation': 0xD058,
            'CenterWeightArea': 0xD059,
            'ExposureBaseMatrix': 0xD05A,
            'ExposureBaseCenter': 0xD05B,
            'ExposureBaseSpot': 0xD05C,
            'LiveViewAFArea': 0xD05D,
            'AELockMode': 0xD05E,
            'AELAFLMode': 0xD05F,
            'LiveViewAFFocus': 0xD061,
            'MeterOff': 0xD062,
            'SelfTimer': 0xD063,
            'MonitorOff': 0xD064,
            'ImgConfTime': 0xD065,
            'AutoOffTimers': 0xD066,
            'AngleLevel': 0xD067,
            'D1ShootingSpeed': 0xD068,
            'D2MaximumShots': 0xD069,
            'ExposureDelayMode': 0xD06A,
            'LongExposureNoiseReduction': 0xD06B,
            'FileNumberSequence': 0xD06C,
            'ControlPanelFinderRearControl': 0xD06D,
            'ControlPanelFinderViewfinder': 0xD06E,
            'D7Illumination': 0xD06F,
            'NrHighISO': 0xD070,
            'SHSetCHGUIDDisp': 0xD071,
            'ArtistName': 0xD072,
            'NikonCopyrightInfo': 0xD073,
            'FlashSyncSpeed': 0xD074,
            'FlashShutterSpeed': 0xD075,
            'E3AAFlashMode': 0xD076,
            'E4ModelingFlash': 0xD077,
            'BracketSet': 0xD078,
            'E6ManualModeBracketing': 0xD079,
            'BracketOrder': 0xD07A,
            'E8AutoBracketSelection': 0xD07B,
            'BracketingSet': 0xD07C,
            'F1CenterButtonShootingMode': 0xD080,
            'CenterButtonPlaybackMode': 0xD081,
            'F2Multiselector': 0xD082,
            'F3PhotoInfoPlayback': 0xD083,
            'F4AssignFuncButton': 0xD084,
            'F5CustomizeCommDials': 0xD085,
            'ReverseCommandDial': 0xD086,
            'ApertureSetting': 0xD087,
            'MenusAndPlayback': 0xD088,
            'F6ButtonsAndDials': 0xD089,
            'NoCFCard': 0xD08A,
            'CenterButtonZoomRatio': 0xD08B,
            'FunctionButton2': 0xD08C,
            'AFAreaPoint': 0xD08D,
            'NormalAFOn': 0xD08E,
            'CleanImageSensor': 0xD08F,
            'ImageCommentString': 0xD090,
            'ImageCommentEnable': 0xD091,
            'ImageRotation': 0xD092,
            'ManualSetLensNo': 0xD093,
            'MovScreenSize': 0xD0A0,
            'MovVoice': 0xD0A1,
            'MovMicrophone': 0xD0A2,
            'MovFileSlot': 0xD0A3,
            'MovRecProhibitCondition': 0xD0A4,
            'ManualMovieSetting': 0xD0A6,
            'MovQuality': 0xD0A7,
            'LiveViewScreenDisplaySetting': 0xD0B2,
            'MonitorOffDelay': 0xD0B3,
            'Bracketing': 0xD0C0,
            'AutoExposureBracketStep': 0xD0C1,
            'AutoExposureBracketProgram': 0xD0C2,
            'AutoExposureBracketCount': 0xD0C3,
            'WhiteBalanceBracketStep': 0xD0C4,
            'WhiteBalanceBracketProgram': 0xD0C5,
            'LensID': 0xD0E0,
            'LensSort': 0xD0E1,
            'LensType': 0xD0E2,
            'FocalLengthMin': 0xD0E3,
            'FocalLengthMax': 0xD0E4,
            'MaxApAtMinFocalLength': 0xD0E5,
            'MaxApAtMaxFocalLength': 0xD0E6,
            'FinderISODisp': 0xD0F0,
            'AutoOffPhoto': 0xD0F2,
            'AutoOffMenu': 0xD0F3,
            'AutoOffInfo': 0xD0F4,
            'SelfTimerShootNum': 0xD0F5,
            'VignetteCtrl': 0xD0F7,
            'AutoDistortionControl': 0xD0F8,
            'SceneMode': 0xD0F9,
            'SceneMode2': 0xD0FD,
            'SelfTimerInterval': 0xD0FE,
            'NikonExposureTime': 0xD100,
            'ACPower': 0xD101,
            'WarningStatus': 0xD102,
            'MaximumShots': 0xD103,
            'AFLockStatus': 0xD104,
            'AELockStatus': 0xD105,
            'FVLockStatus': 0xD106,
            'AutofocusLCDTopMode2': 0xD107,
            'AutofocusArea': 0xD108,
            'FlexibleProgram': 0xD109,
            'LightMeter': 0xD10A,
            'RecordingMedia': 0xD10B,
            'USBSpeed': 0xD10C,
            'CCDNumber': 0xD10D,
            'CameraOrientation': 0xD10E,
            'GroupPtnType': 0xD10F,
            'FNumberLock': 0xD110,
            'ExposureApertureLock': 0xD111,
            'TVLockSetting': 0xD112,
            'AVLockSetting': 0xD113,
            'IllumSetting': 0xD114,
            'FocusPointBright': 0xD115,
            'ExternalFlashAttached': 0xD120,
            'ExternalFlashStatus': 0xD121,
            'ExternalFlashSort': 0xD122,
            'ExternalFlashMode': 0xD123,
            'ExternalFlashCompensation': 0xD124,
            'NewExternalFlashMode': 0xD125,
            'FlashExposureCompensation': 0xD126,
            'HDRMode': 0xD130,
            'HDRHighDynamic': 0xD131,
            'HDRSmoothing': 0xD132,
            'OptimizeImage': 0xD140,
            'Saturation': 0xD142,
            'BWFillerEffect': 0xD143,
            'BWSharpness': 0xD144,
            'BWContrast': 0xD145,
            'BWSettingType': 0xD146,
            'Slot2SaveMode': 0xD148,
            'RawBitMode': 0xD149,
            'ActiveDLighting': 0xD14E,
            'FlourescentType': 0xD14F,
            'TuneColourTemperature': 0xD150,
            'TunePreset0': 0xD151,
            'TunePreset1': 0xD152,
            'TunePreset2': 0xD153,
            'TunePreset3': 0xD154,
            'TunePreset4': 0xD155,
            'BeepOff': 0xD160,
            'AutofocusMode': 0xD161,
            'AFAssist': 0xD163,
            'PADVPMode': 0xD164,
            'ImageReview': 0xD165,
            'AFAreaIllumination': 0xD166,
            'NikonFlashMode': 0xD167,
            'FlashCommanderMode': 0xD168,
            'FlashSign': 0xD169,
            '_ISOAuto': 0xD16A,
            'RemoteTimeout': 0xD16B,
            'GridDisplay': 0xD16C,
            'FlashModeManualPower': 0xD16D,
            'FlashModeCommanderPower': 0xD16E,
            'AutoFP': 0xD16F,
            'DateImprintSetting': 0xD170,
            'DateCounterSelect': 0xD171,
            'DateCountData': 0xD172,
            'DateCountDisplaySetting': 0xD173,
            'RangeFinderSetting': 0xD174,
            'CSMMenu': 0xD180,
            'WarningDisplay': 0xD181,
            'BatteryCellKind': 0xD182,
            'ISOAutoHiLimit': 0xD183,
            'DynamicAFArea': 0xD184,
            'ContinuousSpeedHigh': 0xD186,
            'InfoDispSetting': 0xD187,
            'PreviewButton': 0xD189,
            'PreviewButton2': 0xD18A,
            'AEAFLockButton2': 0xD18B,
            'IndicatorDisp': 0xD18D,
            'CellKindPriority': 0xD18E,
            'BracketingFramesAndSteps': 0xD190,
            'LiveViewMode': 0xD1A0,
            'LiveViewDriveMode': 0xD1A1,
            'LiveViewStatus': 0xD1A2,
            'LiveViewImageZoomRatio': 0xD1A3,
            'LiveViewProhibitCondition': 0xD1A4,
            'MovieShutterSpeed': 0xD1A8,
            'MovieFNumber': 0xD1A9,
            'MovieISO': 0xD1AA,
            'LiveViewMovieMode': 0xD1AC,
            'ExposureDisplayStatus': 0xD1B0,
            'ExposureIndicateStatus': 0xD1B1,
            'InfoDispErrStatus': 0xD1B2,
            'ExposureIndicateLightup': 0xD1B3,
            'FlashOpen': 0xD1C0,
            'FlashCharged': 0xD1C1,
            'FlashMRepeatValue': 0xD1D0,
            'FlashMRepeatCount': 0xD1D1,
            'FlashMRepeatInterval': 0xD1D2,
            'FlashCommandChannel': 0xD1D3,
            'FlashCommandSelfMode': 0xD1D4,
            'FlashCommandSelfCompensation': 0xD1D5,
            'FlashCommandSelfValue': 0xD1D6,
            'FlashCommandAMode': 0xD1D7,
            'FlashCommandACompensation': 0xD1D8,
            'FlashCommandAValue': 0xD1D9,
            'FlashCommandBMode': 0xD1DA,
            'FlashCommandBCompensation': 0xD1DB,
            'FlashCommandBValue': 0xD1DC,
            'ApplicationMode': 0xD1F0,
            'ActiveSlot': 0xD1F2,
            'ActivePicCtrlItem': 0xD200,
            'ChangePicCtrlItem': 0xD201,
            'MovieNrHighISO': 0xD236,
            'D241': 0xD241,
            'D244': 0xD244,
            'D247': 0xD247,
            'GUID': 0xD24F,
            'D250': 0xD250,
            'D251': 0xD251,
            'ISO': 0xF002,
            'ImageCompression': 0xF009,
            'NikonImageSize': 0xF00A,
            'NikonWhiteBalance': 0xF00C,
            # TODO: Are these redundant? Or product-specific?
            '_LongExposureNoiseReduction': 0xF00D,
            'HiISONoiseReduction': 0xF00E,
            '_ActiveDLighting': 0xF00F,
            '_MovQuality': 0xF01C,
        }
        product_properties.update(props)
        return super(Nikon, self)._PropertyCode(
            **product_properties
        )

    def _OperationCode(self, **product_operations):
        return super(Nikon, self)._OperationCode(
            GetProfileAllData=0x9006,
            SendProfileData=0x9007,
            DeleteProfile=0x9008,
            SetProfileData=0x9009,
            AdvancedTransfer=0x9010,
            GetFileInfoInBlock=0x9011,
            Capture=0x90C0,
            AFDrive=0x90C1,
            SetControlMode=0x90C2,
            DelImageSDRAM=0x90C3,
            GetLargeThumb=0x90C4,
            CurveDownload=0x90C5,
            CurveUpload=0x90C6,
            CheckEvents=0x90C7,
            DeviceReady=0x90C8,
            SetPreWBData=0x90C9,
            GetVendorPropCodes=0x90CA,
            AFCaptureSDRAM=0x90CB,
            GetPictCtrlData=0x90CC,
            SetPictCtrlData=0x90CD,
            DelCstPicCtrl=0x90CE,
            GetPicCtrlCapability=0x90CF,
            GetPreviewImg=0x9200,
            StartLiveView=0x9201,
            EndLiveView=0x9202,
            GetLiveViewImg=0x9203,
            MfDrive=0x9204,
            ChangeAFArea=0x9205,
            AFDriveCancel=0x9206,
            InitiateCaptureRecInMedia=0x9207,
            GetVendorStorageIDs=0x9209,
            StartMovieRecInCard=0x920A,
            EndMovieRec=0x920B,
            TerminateCapture=0x920C,
            GetDevicePTPIPInfo=0x90E0,
            GetPartialObjectHiSpeed=0x9400,
            GetDevicePropEx=0x9504,
            **product_operations
        )

    def _ResponseCode(self, **product_responses):
        return super(Nikon, self)._ResponseCode(
            HardwareError=0xA001,
            OutOfFocus=0xA002,
            ChangeCameraModeFailed=0xA003,
            InvalidStatus=0xA004,
            SetPropertyNotSupported=0xA005,
            WbResetError=0xA006,
            DustReferenceError=0xA007,
            ShutterSpeedBulb=0xA008,
            MirrorUpSequence=0xA009,
            CameraModeNotAdjustFNumber=0xA00A,
            NotLiveView=0xA00B,
            MfDriveStepEnd=0xA00C,
            MfDriveStepInsufficiency=0xA00E,
            AdvancedTransferCancel=0xA022,
            **product_responses
        )

    def _EventCode(self, **product_events):
        return super(Nikon, self)._EventCode(
            ObjectAddedInSDRAM=0xC101,
            CaptureCompleteRecInSdram=0xC102,
            AdvancedTransfer=0xC103,
            PreviewImageAdded=0xC104,
            **product_events
        )

    def _FilesystemType(self, **product_filesystem_types):
        return super(Nikon, self)._FilesystemType(
            **product_filesystem_types
        )

    def _NikonEvent(self):
        return PrefixedArray(
            self._UInt16,
            Struct(
                'EventCode' / self._EventCode,
                'Parameter' / self._UInt32,
            )
        )

    def _set_endian(self, endian):
        logger.debug('Set Nikon endianness')
        super(Nikon, self)._set_endian(endian)
        self._NikonEvent = self._NikonEvent()

    # TODO: Add event queue over all transports and extensions.
    def check_events(self):
        '''Check Nikon specific event'''
        ptp = Container(
            OperationCode='CheckEvents',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        return self._parse_if_data(response, self._NikonEvent)

    # TODO: Provide a single camera agnostic command that will trigger a camera
    def capture(self):
        '''Nikon specific capture'''
        ptp = Container(
            OperationCode='Capture',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        return self.mesg(ptp)

    def af_capture_sdram(self):
        '''Nikon specific autofocus and capture to SDRAM'''
        ptp = Container(
            OperationCode='AFCaptureSDRAM',
            SessionID=self._session,
            TransactionID=self._transaction,
            Parameter=[]
        )
        return self.mesg(ptp)

    def event(self, wait=False):
        '''Check Nikon or PTP events

        If `wait` this function is blocking. Otherwise it may return None.
        '''
        # TODO: Do something reasonable on wait=True
        evt = None
        timeout = None if wait else 0.001
        # TODO: Join queues to preserve order of Nikon and PTP events.
        if not self.__event_queue.empty():
            evt = self.__event_queue.get(block=not wait, timeout=timeout)
        else:
            evt = super(Nikon, self).event(wait=wait)

        return evt

    def __nikon_poll_events(self):
        '''Poll events, adding them to a queue.'''
        while (not self.__nikon_event_shutdown.is_set() and
               _main_thread_alive()):
            try:
                evts = self.check_events()
                if evts:
                    for evt in evts:
                        logger.debug('Event queued')
                        self.__event_queue.put(evt)
            except Exception as e:
                logger.error(e)
            sleep(3)
        self.__nikon_event_shutdown.clear()
