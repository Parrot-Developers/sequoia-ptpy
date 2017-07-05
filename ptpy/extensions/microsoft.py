'''This module extends PTP for Microsoft/MTP devices.

Use it in a master module that determines the vendor and automatically uses its
extension. This is why inheritance is not explicit.
'''
import logging
logger = logging.getLogger(__name__)

__all__ = ('Microsoft',)


class Microsoft(object):
    '''This class implements Canon's PTP operations.'''

    def __init__(self, *args, **kwargs):
        logger.debug('Init Microsoft')
        super(Microsoft, self).__init__(*args, **kwargs)

    def _PropertyCode(self, **product_properties):
        return super(Microsoft, self)._PropertyCode(
            SynchronizationPartner=0xD401,
            DeviceFriendlyName=0xD402,
            Volume=0xD403,
            SupportedFormatsOrdered=0xD404,
            DeviceIcon=0xD405,
            SessionInitiatorVendorInfo=0xD406,
            PerceivedDeviceType=0xD407,
            PlaybackRate=0xD410,
            PlaybackObject=0xD411,
            PlaybackContainerIndex=0xD412,
            **product_properties
        )

    def _OperationCode(self, **product_operations):
        return super(Microsoft, self)._OperationCode(
            GetObjectPropsSupported=0x9801,
            GetObjectPropDesc=0x9802,
            GetObjectPropValue=0x9803,
            SetObjectPropValue=0x9804,
            GetObjPropList=0x9805,
            SetObjPropList=0x9806,
            GetInterdependendPropdesc=0x9807,
            SendObjectPropList=0x9808,
            GetObjectReferences=0x9810,
            SetObjectReferences=0x9811,
            UpdateDeviceFirmware=0x9812,
            Skip=0x9820,
            # microsoft.com/WMDRMPD
            GetSecureTimeChallenge=0x9101,
            GetSecureTimeResponse=0x9102,
            SetLicenseResponse=0x9103,
            GetSyncList=0x9104,
            SendMeterChallengeQuery=0x9105,
            GetMeterChallenge=0x9106,
            SetMeterResponse=0x9107,
            CleanDataStore=0x9108,
            GetLicenseState=0x9109,
            SendWMDRMPDCommand=0x910A,
            SendWMDRMPDRequest=0x910B,
            SendWMDRMPDAppRequest=0x9212,
            GetWMDRMPDAppResponse=0x9213,
            EnableTrustedFilesOperations=0x9214,
            DisableTrustedFilesOperations=0x9215,
            EndTrustedAppSession=0x9216,
            # microsoft.com/AAVT
            OpenMediaSession=0x9170,
            CloseMediaSession=0x9171,
            GetNextDataBlock=0x9172,
            SetCurrentTimePosition=0x9173,
            # microsoft.com/WMDRMND: 1.0
            SendRegistrationRequest=0x9180,
            GetRegistrationResponse=0x9181,
            GetProximityChallenge=0x9182,
            SendProximityResponse=0x9183,
            SendWMDRMNDLicenseRequest=0x9184,
            GetWMDRMNDLicenseResponse=0x9185,
            # microsoft.com/WMPPD: 11.1
            ReportAddedDeletedItems=0x9201,
            ReportAcquiredItems=0x9202,
            PlaylistObjectPref=0x9203,
            # microsoft.com/WPDWCN
            ProcessWFCObject=0x9122,
            **product_operations
        )

    def _ResponseCode(self, **product_responses):
        return super(Microsoft, self)._ResponseCode(
            MicrosoftUndefined=0xA800,
            Invalid_ObjectPropCode=0xA801,
            Invalid_ObjectProp_Format=0xA802,
            Invalid_ObjectProp_Value=0xA803,
            Invalid_ObjectReference=0xA804,
            Invalid_Dataset=0xA806,
            Specification_By_Group_Unsupported=0xA807,
            Specification_By_Depth_Unsupported=0xA808,
            Object_Too_Large=0xA809,
            ObjectProp_Not_Supported=0xA80A,
            # microsoft.com/AAVT 1.0,
            Invalid_Media_Session_ID=0xA170,
            Media_Session_Limit_Reached=0xA171,
            No_More_Data=0xA172,
            # microsoft.com/WPDWCN: 1.0,
            Invalid_WFC_Syntax=0xA121,
            WFC_Version_Not_Supported=0xA122,
            **product_responses
        )

    def _EventCode(self, **product_events):
        return super(Microsoft, self)._EventCode(
            ObjectPropChanged=0xC801,
            ObjectPropDescChanged=0xC802,
            ObjectReferencesChanged=0xC803,
            **product_events
        )

    def _FilesystemType(self, **product_filesystem_types):
        return super(Microsoft, self)._FilesystemType(
            **product_filesystem_types
        )

    def _ObjectFormatCode(self, **product_object_formats):
        '''Return desired endianness for known ObjectFormatCode'''
        return super(Microsoft, self)._ObjectFormatCode(
            MediaCard=0xb211,
            MediaCardGroup=0xb212,
            Encounter=0xb213,
            EncounterBox=0xb214,
            M4A=0xb215,
            Firmware=0xb802,
            WindowsImageFormat=0xb881,
            UndefinedAudio=0xb900,
            WMA=0xb901,
            OGG=0xb902,
            AAC=0xb903,
            AudibleCodec=0xb904,
            FLAC=0xb906,
            SamsungPlaylist=0xb909,
            UndefinedVideo=0xb980,
            WMV=0xb981,
            MP4=0xb982,
            MP2=0xb983,
            Mobile3GP=0xb984,
            UndefinedCollection=0xba00,
            AbstractMultimediaAlbum=0xba01,
            AbstractImageAlbum=0xba02,
            AbstractAudioAlbum=0xba03,
            AbstractVideoAlbum=0xba04,
            AbstractAudioVideoPlaylist=0xba05,
            AbstractContactGroup=0xba06,
            AbstractMessageFolder=0xba07,
            AbstractChapteredProduction=0xba08,
            AbstractAudioPlaylist=0xba09,
            AbstractVideoPlaylist=0xba0a,
            AbstractMediacast=0xba0b,
            WPLPlaylist=0xba10,
            M3UPlaylist=0xba11,
            MPLPlaylist=0xba12,
            ASXPlaylist=0xba13,
            PLSPlaylist=0xba14,
            UndefinedDocument=0xba80,
            AbstractDocument=0xba81,
            XMLDocument=0xba82,
            MSWordDocument=0xba83,
            MHTCompiledHTMLDocument=0xba84,
            MSExcelSpreadsheetXLS=0xba85,
            MSPowerpointPresentationPPT=0xba86,
            UndefinedMessage=0xbb00,
            AbstractMessage=0xbb01,
            UndefinedContact=0xbb80,
            AbstractContact=0xbb81,
            vCard2=0xbb82,
            vCard3=0xbb83,
            UndefinedCalendarItem=0xbe00,
            AbstractCalendarItem=0xbe01,
            vCalendar1=0xbe02,
            vCalendar2=0xbe03,
            UndefinedWindowsExecutable=0xbe80,
            MediaCast=0xbe81,
            Section=0xbe82,
            **product_object_formats
        )
