'''This module extends PTPDevice for Canon devices.

Use it in a master module that determines the vendor and automatically uses its
extension:

    from ptp import *
    # Here PTPDevice is unextended
    from vendors.canon import *
    # Here PTPDevice has a vendor extension
    from transport.usb import *
    # Here PTPDevice can now be instantiated over transport
'''
import ptp

__all__ = ('PTPDevice',)


class PTPDevice(ptp.PTPDevice):
    '''This class implements Canon's PTP operations.'''

    def _PropertyCode(self, **product_properties):
        return ptp.PTPDevice._PropertyCode(
            self,
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
        return ptp.PTPDevice._OperationCode(
            self,
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
            EOSGetViewFinderData=0x9153,
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

    def _ResponseCode(self, **product_responses):
        return ptp.PTPDevice._ResponseCode(
            self,
            **product_responses
        )

    def _EventCode(self, **product_events):
        return ptp.PTPDevice._EventCode(
            self,
            CanonDeviceInfoChanged=0xC008,
            CanonRequestObjectTransfer=0xC009,
            CameraModeChanged=0xC00C,
            **product_events
        )

    def _FilesystemType(self, **product_filesystem_types):
        return ptp.PTPDevice._ResponseCode(
            self,
            **product_filesystem_types
        )
