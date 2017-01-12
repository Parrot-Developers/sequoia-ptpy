'''This module extends PTPDevice for Canon devices.

Use it in a master module that determines the vendor and automatically uses its
extension. This is why inheritance is not explicit.
'''
from .. import ptp
from construct import (
    Container, Struct
)
import six

__all__ = ('PTPDevice',)


class PTPDevice(object):
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
        return ptp.PTPDevice._FilesystemType(
            self,
            **product_filesystem_types
        )

    # TODO: Decode Canon specific events and properties.
    def _set_endian(self, endian):
        ptp.PTPDevice._set_endian(self, endian)
        # TODO: Instantiate Canon specific structures here.

    # TODO: implement GetObjectSize
    # TODO: implement SetObjectArchive
    # TODO: implement KeepDeviceOn
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
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        response = self.send(ptp)
        return response

    # TODO: implement EOSSetDevicePropValueEx
    # TODO: implement EOSGetRemoteMode

    def eos_set_remote_mode(self, mode):
        '''Set remote mode on EOS cameras'''

        # TODO: Add automatic translation of remote mode codes and names.
        code = mode
        ptp = Container(
            OperationCode='EOSSetRemoteMode',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[code]
        )
        response = self.send(ptp)
        return response

    def eos_event_mode(self, mode):
        '''Set event mode on EOS cameras'''
        # Canon extension uses this to enrich the events returned by the camera
        # as well as allowing for polling at the convenience of the initiator.

        # TODO: Add automatic translation of event mode codes and names.
        code = mode
        ptp = Container(
            OperationCode='EOSSetEventMode',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[code]
        )
        response = self.send(ptp)
        return response

    def eos_get_event(self):
        '''Poll EOS camera for EOS events'''
        ptp = Container(
            OperationCode='EOSGetEvent',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        response = self.recv(ptp)
        # TODO: parse EOS events automatically
        return response

    # TODO: implement EOSTransferComplete
    # TODO: implement EOSCancelTransfer
    # TODO: implement EOSResetTransfer
    # TODO: implement EOSPCHDDCapacity

    def eos_set_ui_lock(self):
        '''Lock user interface on EOS cameras'''
        ptp = Container(
            OperationCode='EOSSetUILock',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        response = self.send(ptp)
        return response

    def eos_reset_ui_lock(self):
        '''Unlock user interface on EOS cameras'''
        ptp = Container(
            OperationCode='EOSResetUILock',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        response = self.send(ptp)
        return response

    # TODO: implement EOSKeepDeviceOn
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
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        response = self.send(ptp)
        return response

    def eos_bulb_end(self):
        '''End bulb capture on EOS cameras'''
        ptp = Container(
            OperationCode='EOSBulbEnd',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[]
        )
        response = self.send(ptp)
        return response

    # TODO: implement EOSRequestDevicePropValue
    # TODO: implement EOSRemoteReleaseOn
    # TODO: implement EOSRemoteReleaseOff
    # TODO: implement EOSInitiateViewfinder
    # TODO: implement EOSTerminateViewfinder
    # TODO: implement EOSGetViewFinderData
    # TODO: implement EOSDoAf

    def eos_drive_lens(self, infinity=True, steps=1):
        '''
        Drive lens focus on EOS cameras with an auto-focus lens on.


        If `infinity` is `True`, the focal plane is driven away from the camera
        the given number of steps.
        '''

        # TODO: Check these assumptions.
        if steps >= 0x8000:
            steps = 0x8000 - 1
        if steps < 0x0000:
            steps = 0
        instruction = 0x8000 if infinity else 0x0000
        instruction |= steps

        ptp = Container(
            OperationCode='EOSDriveLens',
            SessionID=self.__session,
            TransactionID=self.__transaction,
            Parameter=[instruction]
        )
        response = self.send(ptp)
        return response

    # TODO: implement EOSDepthOfFieldPreview
    # TODO: implement EOSClickWB
    # TODO: implement EOSZoom
    # TODO: implement EOSZoomPosition
    # TODO: implement EOSSetLiveAfFrame
    # TODO: implement EOSAfCancel
    # TODO: implement EOSFAPIMessageTX
    # TODO: implement EOSFAPIMessageRX
