# coding=utf-8
import random
import sys
import time

sys.path.append("./acfun/protos/Im")
import base64
import json
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import proto
from google.protobuf.json_format import MessageToJson
import acfun.protos.Im.TokenInfo_pb2 as TokenInfo_pb2
import acfun.protos.Im.PacketHeader_pb2 as PacketHeader_pb2
import acfun.protos.Im.UpstreamPayload_pb2 as UpstreamPayload_pb2
import acfun.protos.Im.DownstreamPayload_pb2 as DownstreamPayload_pb2
import acfun.protos.Im.RegisterRequest_pb2 as Register_pb2
import acfun.protos.Im.RegisterResponse_pb2 as RegisterResponse_pb2
import acfun.protos.Im.ErrorMessage_pb2 as ErrorMessage_pb2
import acfun.protos.Im.KeepAliveRequest_pb2 as KeepAliveRequest_pb2
import acfun.protos.Im.KeepAliveResponse_pb2 as KeepAliveResponse_pb2
import acfun.protos.Im.ClientConfigGetResponse_pb2 as ClientConfigGetResponse_pb2
import acfun.protos.Im.SessionListResponse_pb2 as SessionListResponse_pb2
import acfun.protos.Im.GroupMemberListGetRequest_pb2 as GroupMemberListGetRequest_pb2
import acfun.protos.Im.GroupMemberListGetResponse_pb2 as GroupMemberListGetResponse_pb2
import acfun.protos.Im.PullOldRequest_pb2 as PullOldRequest_pb2
import acfun.protos.Im.PullOldResponse_pb2 as PullOldResponse_pb2
import acfun.protos.Im.Message_pb2 as Message_pb2


# AES Padding
# https://blog.csdn.net/qq_39727936/article/details/114494791

# proto-plus
# https://proto-plus-python.readthedocs.io/en/latest/index.html


def protos_to_dict(p):
    return json.loads(MessageToJson(p))


class ErrorMessage(proto.Message):
    errorCode = proto.Field(proto.INT32, number=3)
    errorMessage = proto.Field(proto.STRING, number=5)


class ClientConfigGetRequest(proto.Message):
    version = proto.Field(proto.UINT32, number=1)


class MessageContent(proto.Message):
    content = proto.Field(proto.STRING, number=1)


class User(proto.Message):
    appId = proto.Field(proto.INT32, number=1)
    uid = proto.Field(proto.INT64, number=2)


def proto_user_serialize(uid: int):
    user = User()
    user.appId = 13
    user.uid = uid
    return User.serialize(user)


class AcProtos:
    seqId = 0
    header_offset = 12
    payload_offset = 16
    command_map = {
        "Basic.Register": 'Basic_Register_Response',
        "Basic.KeepAlive": 'Keep_Alive_Response',
        "Basic.ClientConfigGet": 'Basic_ClientConfigGet_Response',
        "Message.Session": 'Message_Session_Response',
        "Group.UserGroupList": 'Group_UserGroupList_Response',
        "Message.PullOld": 'Message_PullOld_Response',
        "Message.Send": 'Message_Response',
        "Push.Message": 'Message_Response',
    }

    def __init__(self, acws):
        self.acws = acws
        self.config = acws.config
        pass

    def _aes_encrypt(self, key, payload):
        key = base64.standard_b64decode(key)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        payload = pad(payload, AES.block_size, 'pkcs7')
        result = cipher.encrypt(payload)
        return iv + result

    def _aes_decrypt(self, key, data):
        key = base64.standard_b64decode(key)
        iv = data[:self.payload_offset]
        payload = data[self.payload_offset:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        result = cipher.decrypt(payload)
        return unpad(result, AES.block_size, 'pkcs7')

    def debug(self, key, b64msg: (str, bytes), up: bool = False):
        message = base64.standard_b64decode(b64msg)
        packet_header_len = int.from_bytes(message[4:8], byteorder='big')
        payload_len = int.from_bytes(message[8:12], byteorder='big')
        print(f"packet_header_len: {packet_header_len} {message[4:8].hex()}")
        print(f"payload_len: {payload_len} {message[8:12].hex()}")
        packet_header = PacketHeader_pb2.PacketHeader()
        header = message[self.header_offset:self.header_offset + packet_header_len]
        packet_header.ParseFromString(header)
        print(packet_header)
        print("=" * 40)
        body = message[self.header_offset + packet_header_len:]
        print(f"recv body {len(body)}: ", body)
        print("recv body[b64]: ", base64.standard_b64encode(body))
        payload_data = message[self.header_offset + packet_header_len:]
        decrypted_data = self._aes_decrypt(key, payload_data)
        print(f"decrypted_data {len(decrypted_data)}: {decrypted_data}")
        print(f"decrypted_data[b64]: {base64.standard_b64encode(decrypted_data)}")
        if up is True:
            upstream_payload = UpstreamPayload_pb2.UpstreamPayload()
            upstream_payload.ParseFromString(decrypted_data)
            print("#" * 40)
            print(upstream_payload)
            print("#" * 40)
        else:
            downstream_payload = DownstreamPayload_pb2.DownstreamPayload()
            downstream_payload.FromString(decrypted_data)
            print("#" * 40)
            print(downstream_payload)
            print("#" * 40)

    def decode(self, message: bytes):
        # print(f"total length: {len(message)}")
        packet_header_len = int.from_bytes(message[4:8], byteorder='big')
        payload_len = int.from_bytes(message[8:12], byteorder='big')
        # print(f"packet_header_len: {packet_header_len} {message[4:8].hex()}")
        # print(f"payload_len: {payload_len} {message[8:12].hex()}")
        packet_header = PacketHeader_pb2.PacketHeader()
        header = message[self.header_offset:self.header_offset + packet_header_len]
        packet_header.ParseFromString(header)
        # print(packet_header)
        # print("=" * 40)
        payload_data = message[self.header_offset + packet_header_len:]
        # print(f"packet_header.encryptionMode: {packet_header.encryptionMode}")
        if packet_header.encryptionMode == 1:  # kEncryptionServiceToken
            decrypted_data = self._aes_decrypt(self.config.ssecurity, payload_data)
        elif packet_header.encryptionMode == 2:  # kEncryptionSessionKey
            decrypted_data = self._aes_decrypt(self.config.sessKey, payload_data)
        else:  # kEncryptionNone
            decrypted_data = payload_data
            stream_payload = ErrorMessage.deserialize(decrypted_data)
            print(stream_payload)
            raise BufferError(stream_payload.errorMessage)
        # decrypted_data = decrypted_data[:packet_header.decodedPayloadLen]
        # print(f"decrypted_data[{len(decrypted_data)}]: ", decrypted_data)
        # print(f"decrypted_data[b64]: {base64.standard_b64encode(decrypted_data)}")
        if self.seqId < 2:
            stream_payload = UpstreamPayload_pb2.UpstreamPayload()
        else:
            stream_payload = DownstreamPayload_pb2.DownstreamPayload()
        stream_payload.ParseFromString(decrypted_data)
        # print("#" * 40)
        # print(f"Command: {stream_payload.command}")
        # print("#" * 40)
        if stream_payload.errorCode:
            print(stream_payload)
            raise ValueError(f"[{stream_payload.errorCode}] {stream_payload.errorMsg}")
        command = stream_payload.command
        func_name = self.command_map.get(command)
        assert func_name is not None
        return getattr(self, func_name)(packet_header, stream_payload)

    def encode(self, key_n: int, command, payload_bytes: bytes):
        token_info = TokenInfo_pb2.TokenInfo()
        token_info.tokenType = 1
        if self.config.acer.is_logined:
            token_info.token = self.config.api_st
        else:
            token_info.token = self.config.visitor_st
        header = PacketHeader_pb2.PacketHeader()
        header.appId = self.config.appId
        header.uid = self.config.userId
        header.instanceId = self.config.instanceId
        payload_len = len(payload_bytes)
        encrypted = payload_bytes
        if key_n in [1, 2]:
            key = self.config.ssecurity if key_n == 1 else self.config.sessKey
            encrypted = self._aes_encrypt(key, payload_bytes)
        header.decodedPayloadLen = payload_len
        header.encryptionMode = key_n
        header.tokenInfo.CopyFrom(token_info)
        header.seqId = self.seqId
        header.kpn = b"ACFUN_APP"
        header_payload = header.SerializeToString()
        return self.seqId, command, b"".join([
            bytes.fromhex("abcd0001"),
            len(header_payload).to_bytes(4, "big"),
            len(encrypted).to_bytes(4, "big"),
            header_payload,
            encrypted
        ])

    def upstream(self, command, payload):
        upstream_payload = UpstreamPayload_pb2.UpstreamPayload()
        upstream_payload.command = command
        upstream_payload.seqId = self.seqId
        upstream_payload.payloadData = payload
        payload_body = upstream_payload.SerializeToString()
        return command, payload_body

    def Basic_Register_Request(self):
        self.seqId += 1
        payload = Register_pb2.RegisterRequest()
        app_info = Register_pb2.AppInfo__pb2.AppInfo()
        app_info.sdkVersion = "kwai-acfun-live-link"
        app_info.linkVersion = "2.13.8"
        payload.appInfo.CopyFrom(app_info)
        device_info = Register_pb2.DeviceInfo__pb2.DeviceInfo()
        device_info.platformType = 9
        device_info.deviceModel = "h5"
        if self.config.acer.is_logined:
            device_info.deviceId = self.config.did
        payload.deviceInfo.CopyFrom(device_info)
        payload.presenceStatus = 1
        payload.appActiveStatus = 1
        ztcommon_info = Register_pb2.ZtCommonInfo__pb2.ZtCommonInfo()
        ztcommon_info.kpn = "ACFUN_APP"
        ztcommon_info.kpf = "PC_WEB"
        ztcommon_info.uid = int(self.config.userId)
        if self.config.acer.is_logined:
            ztcommon_info.did = self.config.did
        payload.instanceId = self.config.instanceId
        payload.ztCommonInfo.CopyFrom(ztcommon_info)
        upstream_payload = UpstreamPayload_pb2.UpstreamPayload()
        upstream_payload.command = "Basic.Register"
        upstream_payload.seqId = self.seqId
        upstream_payload.retryCount = 1
        upstream_payload.payloadData = payload.SerializeToString()
        upstream_payload.subBiz = "mainApp"
        payload_body = upstream_payload.SerializeToString()
        return self.encode(1, "Basic.Register", payload_body)

    def Basic_Register_Response(self, packet_header, stream_payload):
        reg_resp = RegisterResponse_pb2.RegisterResponse()
        reg_resp.ParseFromString(stream_payload.payloadData)
        self.config.appId = packet_header.appId
        self.config.instanceId = packet_header.instanceId
        self.config.sessKey = base64.standard_b64encode(reg_resp.sessKey)
        self.acws.task(*self.Basic_ClientConfigGet())
        self.acws.is_register_done = True
        print(f"did: {self.config.did}")
        print(f"userId: {self.config.userId}")
        print(f"ssecurity: {self.config.ssecurity}")
        print(f"sessKey: {self.config.sessKey.decode()}")
        print(">>>>>>>>>AcWebsocket Registed<<<<<<<<<")
        return packet_header.seqId, stream_payload.command, MessageToJson(reg_resp)

    def Basic_ClientConfigGet(self):
        self.seqId += 1
        payload = ClientConfigGetRequest()
        payload.version = 0
        payload_body = self.upstream("Basic.ClientConfigGet", ClientConfigGetRequest.serialize(payload))
        return self.encode(2, *payload_body)

    def Basic_ClientConfigGet_Response(self, packet_header, stream_payload):
        payload = ClientConfigGetResponse_pb2.ClientConfigGetResponse()
        payload.ParseFromString(stream_payload.payloadData)
        # todo saved configs
        self.acws.task(*self.Keep_Alive_Request())
        return packet_header.seqId, stream_payload.command, protos_to_dict(payload)

    def Keep_Alive_Request(self):
        self.seqId += 1
        payload = KeepAliveRequest_pb2.KeepAliveRequest()
        payload.presenceStatus = 1
        payload.appActiveStatus = 1
        payload.keepaliveIntervalSec = 120
        payload_body = self.upstream("Basic.KeepAlive", payload.SerializeToString())
        return self.encode(2, *payload_body)

    def Keep_Alive_Response(self, packet_header, stream_payload):
        payload = KeepAliveResponse_pb2.KeepAliveResponse()
        payload.ParseFromString(stream_payload.payloadData)
        return packet_header.seqId, stream_payload.command, protos_to_dict(payload)

    def Basic_ping(self):
        self.seqId += 1
        return self.encode(2, *self.upstream("Basic.Ping", b""))

    def Message_Session(self):
        self.seqId += 1
        raw = bytes([16, 0])
        payload_body = self.upstream("Message.Session", raw)
        return self.encode(2, *payload_body)

    def Message_Session_Response(self, packet_header, stream_payload):
        payload = SessionListResponse_pb2.SessionListResponse()
        payload.ParseFromString(stream_payload.payloadData)
        session_data = protos_to_dict(payload)
        return packet_header.seqId, stream_payload.command, session_data

    def Group_UserGroupList(self):
        self.seqId += 1
        payload = GroupMemberListGetRequest_pb2.GroupMemberListGetRequest()
        payload.groupId = b"0"
        sync_cookie_payload = GroupMemberListGetRequest_pb2.SyncCookie__pb2.SyncCookie()
        sync_cookie_payload.syncOffset = -1
        payload.syncCookie.CopyFrom(sync_cookie_payload)
        payload_body = self.upstream("Group.UserGroupList", payload.SerializeToString())
        return self.encode(2, *payload_body)

    def Group_UserGroupList_Response(self, packet_header, stream_payload):
        payload = GroupMemberListGetResponse_pb2.GroupMemberListGetResponse()
        payload.ParseFromString(stream_payload.payloadData)
        return packet_header.seqId, stream_payload.command, protos_to_dict(payload)

    def Message_PullOld_Request(self, uid: int, minSeq: int, maxSeq: int, count: int = 10):
        self.seqId += 1
        payload = PullOldRequest_pb2.PullOldRequest()
        payload.target.ParseFromString(proto_user_serialize(uid))
        payload.minSeq = minSeq
        payload.maxSeq = maxSeq
        payload.count = count
        payload_body = self.upstream("Message.PullOld", payload.SerializeToString())
        return self.encode(2, *payload_body)

    def Message_PullOld_Response(self, packet_header, stream_payload):
        payload = PullOldResponse_pb2.PullOldResponse()
        payload.ParseFromString(stream_payload.payloadData)
        result = protos_to_dict(payload)
        return packet_header.seqId, stream_payload.command, result

    def Message_Request(self, target_uid: int, content: str):
        self.seqId += 1
        payload = Message_pb2.Message()
        # payload.seqId = int(f"{time.time():.0f}{1:0>6}")
        payload.clientSeqId = int(f"{time.time():.0f}{1:0>6}")
        payload.timestampMs = int(f"{time.time():.0f}{1:0>3}")
        payload.fromUser.ParseFromString(proto_user_serialize(self.config.userId))
        payload.targetId = target_uid
        payload.toUser.ParseFromString(proto_user_serialize(target_uid))
        msg = MessageContent()
        msg.content = content.encode()
        payload.content = MessageContent.serialize(msg)
        payload.strTargetId = str(target_uid)
        payload_body = self.upstream("Message.Send", payload.SerializeToString())
        return self.encode(2, *payload_body)

    def Message_Response(self, packet_header, stream_payload):
        payload = Message_pb2.Message()
        payload.ParseFromString(stream_payload.payloadData)
        return packet_header.seqId, stream_payload.command, protos_to_dict(payload)
