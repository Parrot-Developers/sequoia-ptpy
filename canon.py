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
            StartShootingMode=0x9008,
            EndShootingMode=0x9009,
            ViewfinderOn=0x900B,
            ViewfinderOff=0x900C,
            ReflectChanges=0x900D,
            CheckEvent=0x9013,
            FocusLock=0x9014,
            FocusUnlock=0x9015,
            InitiateCaptureInMemory=0x901A,
            CanonGetPartialObject=0x901B,
            GetViewfinderImage=0x901d,
            GetChanges=0x9020,
            GetFolderEntries=0x9021,
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
