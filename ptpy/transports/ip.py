'''This module implements the IP transport layer for PTP.

It exports the IPTransport class. Both the transport layer and the basic PTP
implementation are Vendor agnostic. Vendor extensions should extend these to
support more operations.
'''
from __future__ import absolute_import
from ..ptp import PTPError
from construct import (
    Array, Bytes, Container, Embedded, Enum, ExprAdapter, Range, Struct,
    Int16ul, Int32ul, Int64ul, Int8ul, RepeatUntil, ListContainer, Debugger,
    Switch, Pass
)
from six.moves.queue import Queue
import six
import socket
import logging

logger = logging.getLogger(__name__)

__all__ = ('IPTransport')
__author__ = 'Luis Mario Domenzain'

# TODO: Implement discovery mechanisms for PTP/IP like zeroconf.


class IPTransport(object):
    '''Implement IP transport.'''
    def __init__(self, device=None):
        '''Instantiate the first available PTP device over IP'''
        self.__setup_constructors()
        logger.debug('Init IP')

        if device is None:
            raise NotImplementedError(
                'IP discovery not implemented. Please provide a device.'
            )

        if type(device) is tuple:
            host, port = device
            self.__setup_connection(host, port)
        else:
            self.__setup_connection(device)

        # Establish Command/Data Connection.
        # Establish Event Connection.
        self.__event_queue = Queue()

    def __setup_connection(self, host=None, port=15740):
        '''Establish a PTP/IP session for a given host'''
        logger.debug(
            'Establishing PTP/IP connection with {}:{}'
            .format(host, port)
        )
        socket.setdefaulttimeout(5)
        hdrlen = self.__Header.sizeof()
        # Command Connection Establishment
        self.__cmdcon = socket.create_connection((host, port))
        self.__cmdcon.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        # Send InitCommand
        # TODO: Allow users to identify as an arbitrary initiator.
        init_cmd_req_payload = self.__InitCommand.build(
            Container(
                InitiatorGUID=16*[0xFF],
                InitiatorFriendlyName='PTPy',
                InitiatorProtocolVersion=Container(
                    Major=100,
                    Minor=000,
                ),
            ))
        init_cmd_req = self.__Packet.build(
            Container(
                Type='InitCommand',
                Payload=init_cmd_req_payload,
            )
        )
        self.__cmdcon._sock.sendall(init_cmd_req)
        # Get ACK/NACK
        init_cmd_req_rsp = self.__cmdcon._sock.recv(72)
        init_cmd_rsp_hdr = self.__Header.parse(
            init_cmd_req_rsp[0:hdrlen]
        )

        if init_cmd_rsp_hdr.Type == 'InitCommandAck':
            cmd_ack = self.__InitCommandACK.parse(init_cmd_req_rsp[hdrlen:])
            logger.debug(
                'Command connection ({}) established'
                .format(cmd_ack.ConnectionNumber)
            )
        elif init_cmd_rsp_hdr.Type == 'InitFail':
            cmd_nack = self.__InitFail.parse(init_cmd_req_rsp[hdrlen:])
            msg = 'InitCommand failed, Reason: {}'.format(
                cmd_nack
            )
            logger.error(msg)
            raise PTPError(msg)
        else:
            msg = 'Unexpected response Type to InitCommand : {}'.format(
                init_cmd_rsp_hdr.Type
            )
            logger.error(msg)
            raise PTPError(msg)

        # Event Connection Establishment
        self.__evtcon = socket.create_connection((host, port))
        self.__evtcon.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # Send InitEvent
        payload = self.__InitEvent.build(Container(
            ConnectionNumber=cmd_ack.ConnectionNumber,
        ))
        evt_req = self.__Packet.build(
            Container(
                Type='InitEvent',
                Payload=payload,
            )
        )
        self.__evtcon._sock.sendall(evt_req)
        # Get ACK/NACK
        init_evt_req_rsp = self.__evtcon._sock.recv(
            hdrlen + self.__InitFail.sizeof()
        )
        init_evt_rsp_hdr = self.__Header.parse(
            init_evt_req_rsp[0:hdrlen]
        )

        if init_evt_rsp_hdr.Type == 'InitEventAck':
            logger.debug(
                'Event connection ({}) established'
                .format(cmd_ack.ConnectionNumber)
            )
        elif init_evt_rsp_hdr.Type == 'InitFail':
            evt_nack = self.__InitFail.parse(init_evt_req_rsp[hdrlen:])
            msg = 'InitEvent failed, Reason: {}'.format(
                evt_nack
            )
            logger.error(msg)
            raise PTPError(msg)
        else:
            msg = 'Unexpected response Type to InitEvent : {}'.format(
                init_evt_rsp_hdr.Type
            )
            logger.error(msg)
            raise PTPError(msg)

    # Helper methods.
    # ---------------------
    def __setup_constructors(self):
        '''Set endianness and create transport-specific constructors.'''
        # Set endianness of constructors before using them.
        self._set_endian('little')

        self.__Length = Int32ul
        self.__Type = Enum(
            Int32ul,
            Undefined=0x00000000,
            InitCommand=0x00000001,
            InitCommandAck=0x00000002,
            InitEvent=0x00000003,
            InitEventAck=0x00000004,
            InitFail=0x00000005,
            Command=0x00000006,
            Response=0x00000007,
            Event=0x00000008,
            StartData=0x00000009,
            Data=0x0000000A,
            Cancel=0x0000000B,
            EndData=0x0000000C,
            Ping=0x0000000D,
            Pong=0x0000000E,
        )
        self.__Header = Struct(
            'Length' / self.__Length,
            'Type' / self.__Type,
        )
        self.__Param = Range(0, 5, self._Parameter)
        self.__EventParam = Range(0, 3, self._Parameter)
        self.__PacketBase = Struct(
            Embedded(self.__Header),
            'Payload' / Bytes(
                lambda ctx, h=self.__Header: ctx.Length - h.sizeof()),
        )
        self.__Packet = ExprAdapter(
            self.__PacketBase,
            encoder=lambda obj, ctx, h=self.__Header: Container(
                Length=len(obj.Payload) + h.sizeof(),
                **obj
            ),
            decoder=lambda obj, ctx: obj,
        )
        # Yet another arbitrary string type. Max-length CString utf8-encoded
        self.__PTPIPString = ExprAdapter(
            RepeatUntil(
                lambda obj, ctx, lst:
                six.unichr(obj) in '\x00' or len(lst) == 40, Int16ul
            ),
            encoder=lambda obj, ctx:
            [] if len(obj) == 0 else[ord(c) for c in six.text_type(obj)]+[0],
            decoder=lambda obj, ctx:
            u''.join(
                [six.unichr(o) for o in obj]
            ).split('\x00')[0],
        )
        # PTP/IP packets
        # Command
        self.__ProtocolVersion = Struct(
            'Minor' / Int16ul,
            'Major' / Int16ul,
        )
        self.__InitCommand = Embedded(Struct(
            'InitiatorGUID' / Array(16, Int8ul),
            'InitiatorFriendlyName' / self.__PTPIPString,
            'InitiatorProtocolVersion' / self.__ProtocolVersion,
        ))
        self.__InitCommandACK = Embedded(Struct(
            'ConnectionNumber' / Int32ul,
            'ResponderGUID' / Array(16, Int8ul),
            'ResponderFriendlyName' / self.__PTPIPString,
            'ResponderProtocolVersion' / self.__ProtocolVersion,
        ))
        # Event
        self.__InitEvent = Embedded(Struct(
            'ConnectionNumber' / Int32ul,
        ))
        # Common to Events and Command requests
        self.__Reason = Enum(
            # TODO: Verify these codes...
            Int32ul,
            Undefined=0x0000,
            RejectedInitiator=0x0001,
            Busy=0x0002,
            Unspecified=0x0003,
        )
        self.__InitFail = Embedded(Struct(
            'Reason' / self.__Reason,
        ))

        self.__DataphaseInfo = Enum(
            Int32ul,
            Undefined=0x00000000,
            In=0x00000001,
            Out=0x00000002,
        )
        self.__Command = Embedded(Struct(
            'DataphaseInfo' / self.__DataphaseInfo,
            'OperationCode' / self._OperationCode,
            'TransactionID' / self._TransactionID,
            'Parameter' / self.__Param,
        ))
        self.__Response = Embedded(Struct(
            'ResponseCode' / self._ResponseCode,
            'TransactionID' / self._TransactionID,
            'Parameter' / self.__Param,
        ))
        self.__Event = Embedded(Struct(
            'EventCode' / self._EventCode,
            'TransactionID' / self._TransactionID,
            'Parameter' / self.__EventParam,
        ))
        self.__StartData = Embedded(Struct(
            'TransactionID' / self._TransactionID,
            'TotalDataLength' / Int64ul,
        ))
        # TODO: Fix packing and unpacking dataphase data
        self.__Data = Embedded(Struct(
            'TransactionID' / self._TransactionID,
            'Data' / Bytes(
                lambda ctx:
                ctx._.Length -
                self.__Header.sizeof() -
                self._TransactionID.sizeof()
            ),
        ))
        self.__EndData = Embedded(Struct(
            'TransactionID' / self._TransactionID,
            'Data' / Bytes(
                lambda ctx:
                ctx._.Length -
                self.__Header.sizeof() -
                self._TransactionID.sizeof()
            ),
        ))
        self.__Cancel = Embedded(Struct(
            'TransactionID' / self._TransactionID,
        ))
        # Convenience construct for parsing packets

        self.__PacketPayload = Debugger(Struct(
            'Header' / Embedded(self.__Header),
            'Payload' / Embedded(Switch(
                lambda ctx: ctx.Type,
                {
                    'InitCommand': self.__InitCommand,
                    'InitCommandAck': self.__InitCommandACK,
                    'InitEvent': self.__InitEvent,
                    'InitFail': self.__InitFail,
                    'Command': self.__Command,
                    'Response': self.__Response,
                    'Event': self.__Event,
                    'StartData': self.__StartData,
                    'Data': self.__Data,
                    'EndData': self.__EndData,
                },
                default=Pass,
            ))
        ))

    def __parse_response(self, ipdata):
        '''Helper method for parsing data.'''
        # Build up container with all PTP info.
        response = self.__PacketPayload.parse(ipdata)
        # Sneak in an implicit Session ID
        response['SessionID'] = self.session_id
        return response

    def __recv(self, event=False, wait=False, raw=False):
        '''Helper method for receiving packets.'''
        ip = self.__evtcon._sock if event else self.__cmdcon._sock
        hdrlen = self.__Header.sizeof()

        data = bytes()
        while True:
            ipdata = ip.recv(hdrlen)
            # Read a single entire packet
            while len(ipdata) < hdrlen:
                ipdata += ip.recv(hdrlen - len(ipdata))
            header = self.__Header.parse(
                ipdata[0:hdrlen]
            )
            while len(ipdata) < header.Length:
                ipdata += ip.recv(header.Length - len(ipdata))
            # Run sanity checks.
            if header.Type not in [
                    'Cancel',
                    'Data',
                    'Event',
                    'Response',
                    'StartData',
                    'EndData',
            ]:
                raise PTPError(
                    'Unexpected PTP/IP packet type {}'
                    .format(header.Type)
                )
            if header.Type not in ['StartData', 'Data', 'EndData']:
                break
            else:
                response = self.__parse_response(ipdata)

            if header.Type == 'StartData':
                expected = response.TotalDataLength
                current_transaction = response.TransactionID
            elif header.Type == 'Data' and response.TransactionID == current_transaction:
                data += response.Data
            elif header.Type == 'EndData' and response.TransactionID == current_transaction:
                data += response.Data
                datalen = len(data)
                if datalen != expected:
                    logger.warning(
                        '{} data than expected {}/{}'
                        .format(
                            'More' if datalen > expected else 'Less',
                            datalen,
                            expected
                        )
                    )
                response['Data'] = data
                response['Type'] = 'Data'
                return response

        if raw:
            # TODO: Deal with raw Data packets??
            return ipdata
        else:
            return self.__parse_response(ipdata)

    def __send(self, ptp_container, event=False):
        '''Helper method for sending packets.'''
        ip = self.__evtcon._sock if event else self.__cmdcon._sock
        packet = self.__Packet.build(ptp_container)
        while ip.sendall(packet) is not None:
            logger.debug('Failed to send {} packet'.format(ptp_container.Type))


    def __send_request(self, ptp_container):
        '''Send PTP request without checking answer.'''
        # Don't modify original container to keep abstraction barrier.
        ptp = Container(**ptp_container)

        # Send unused parameters always
        ptp['Parameter'] += [0] * (5 - len(ptp.Parameter))

        # Send request
        ptp['Type'] = 'Command'
        ptp['DataphaseInfo'] = 'In'
        ptp['Payload'] = self.__Command.build(ptp)
        self.__send(ptp)

    def __send_data(self, ptp_container, data):
        '''Send data without checking answer.'''
        # Don't modify original container to keep abstraction barrier.
        ptp = Container(**ptp_container)
        # Send data
        ptp['Type'] = 'Data'
        ptp['DataphaseInfo'] = 'Out'
        ptp['Payload'] = data
        self.__send(ptp)

    # Actual implementation
    # ---------------------
    def send(self, ptp_container, data):
        '''Transfer operation with dataphase from initiator to responder'''
        logger.debug('SEND {}{}'.format(
            ptp_container.OperationCode,
            ' ' + str(list(map(hex, ptp_container.Parameter)))
            if ptp_container.Parameter else '',
        ))
        self.__send_request(ptp_container)
        self.__send_data(ptp_container, data)
        # Get response and sneak in implicit SessionID and missing parameters.
        return self.__recv()

    def recv(self, ptp_container):
        '''Transfer operation with dataphase from responder to initiator.'''
        logger.debug('RECV {}{}'.format(
            ptp_container.OperationCode,
            ' ' + str(list(map(hex, ptp_container.Parameter)))
            if ptp_container.Parameter else '',
        ))
        self.__send_request(ptp_container)
        dataphase = self.__recv()
        if hasattr(dataphase, 'Data'):
            response = self.__recv()
            if (
                    (ptp_container.TransactionID != dataphase.TransactionID) or
                    (ptp_container.SessionID != dataphase.SessionID) or
                    (dataphase.TransactionID != response.TransactionID) or
                    (dataphase.SessionID != response.SessionID)
            ):
                raise PTPError(
                    'Dataphase does not match with requested operation.'
                )
            response['Data'] = dataphase.Data
            return response
        else:
            return dataphase

    def mesg(self, ptp_container):
        '''Transfer operation without dataphase.'''
        self.__send_request(ptp_container)
        # Get response and sneak in implicit SessionID and missing parameters
        # for FullResponse.
        return self.__recv()

    def event(self, wait=False):
        '''Check event.

        If `wait` this function is blocking. Otherwise it may return None.
        '''
        evt = None
        ipdata = None
        timeout = None if wait else 0.001
        if not self.__event_queue.empty():
            ipdata = self.__event_queue.get(block=not wait, timeout=timeout)
        if ipdata is not None:
            evt = self.__parse_response(ipdata)

        return evt
