# coding=utf-8
import sys
import time
import json
import proto
import base64
import random
import filetype
import blackboxprotobuf
from hashlib import md5
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from acfun.source import apis
from google.protobuf.json_format import MessageToJson
from google.protobuf.pyext.cpp_message import GeneratedProtocolMessageType
from google.protobuf.pyext._message import MessageMeta
from . import PacketHeader_pb2, \
    UpstreamPayload_pb2, DownstreamPayload_pb2, \
    RegisterRequest_pb2, RegisterResponse_pb2, \
    ClientConfigGetRequest_pb2, ClientConfigGetResponse_pb2, \
    KeepAliveRequest_pb2, KeepAliveResponse_pb2, \
    GroupMemberListGetRequest_pb2, GroupMemberListGetResponse_pb2, \
    PullOldRequest_pb2, PullOldResponse_pb2, \
    SessionListResponse_pb2, SessionCreateRequest_pb2, \
    SessionCreateResponse_pb2, SessionRemoveRequest_pb2, \
    ErrorMessage_pb2, Message_pb2, Image_pb2


class ErrorMessage(proto.Message):
    errorCode = proto.Field(proto.INT32, number=3)
    errorMessage = proto.Field(proto.STRING, number=5)


def message_content_serialize(content: str):
    class MessageContent(proto.Message):
        content = proto.Field(proto.STRING, number=1)
    msg = MessageContent()
    msg.content = content.encode()
    return MessageContent.serialize(msg)


def proto_user_serialize(uid: int):
    class User(proto.Message):
        appId = proto.Field(proto.INT32, number=1)
        uid = proto.Field(proto.INT64, number=2)
    user = User()
    user.appId = 13
    user.uid = uid
    return User.serialize(user)


def acim_image_uploader(client, api_st: str, to_uid: str, image_data: bytes):
    md5_hex = md5(image_data).digest()
    head = {
        "Content-Type": filetype.guess_mime(image_data),
        "Content-MD5": base64.standard_b64encode(md5_hex),
        "file-type": filetype.guess_extension(image_data),
        "target": f"{to_uid}",
        "download-verify-type": "1",
    }
    param = {'kpn': "ACFUN_APP", 'acfun.midground.api_st': api_st}
    post_req = client.post(apis['im_image_upload'], params=param, headers=head, data=image_data)
    return post_req.json()


class AcImProtos:
    seqId = 0
    header_offset = 12
    payload_offset = 16
    client_config = {}
    command_rules = {
        "Basic.ClientConfigGet": ClientConfigGetResponse_pb2.ClientConfigGetResponse,
        "Basic.KeepAlive": KeepAliveResponse_pb2.KeepAliveResponse,
        "Message.Session": SessionListResponse_pb2.SessionListResponse,
        "Group.UserGroupList": GroupMemberListGetResponse_pb2.GroupMemberListGetResponse,
        "Message.PullOld": PullOldResponse_pb2.PullOldResponse,
        "Session.Create": SessionCreateResponse_pb2.SessionCreateResponse,
        "Message.Send": Message_pb2.Message,
        "Push.Message": Message_pb2.Message,
        "Message.SessionRemove": None,
    }

    def __init__(self, acws):
        self.acws = acws
        self.config = acws.config

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
            raise BufferError(self.seqId, stream_payload.errorMessage)
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
        proto_class = self.command_rules.get(command)
        if command == "Basic.Register":
            return self.BasicRegister_Response(packet_header, stream_payload)
        elif isinstance(proto_class, GeneratedProtocolMessageType):
            return self.message_response(proto_class, packet_header, stream_payload)
        return self.unknown_response(packet_header, stream_payload)

    def BasicRegister_Response(self, packet_header, stream_payload):
        reg_resp = RegisterResponse_pb2.RegisterResponse()
        reg_resp.ParseFromString(stream_payload.payloadData)
        self.config.appId = packet_header.appId
        self.config.instanceId = packet_header.instanceId
        self.config.sessKey = base64.standard_b64encode(reg_resp.sessKey)
        return packet_header.seqId, stream_payload.command, MessageToJson(reg_resp)

    def message_response(self, proto_class, packet_header, stream_payload):
        payload = proto_class()
        payload.ParseFromString(stream_payload.payloadData)
        return packet_header.seqId, stream_payload.command, json.loads(MessageToJson(payload))

    def unknown_response(self, packet_header, stream_payload):
        message, typedef = blackboxprotobuf.protobuf_to_json(stream_payload.payloadData)
        if stream_payload.command not in self.command_rules:
            print(f"[seqId:{packet_header.seqId}] {stream_payload.command}")
            print(typedef)
            print(message)
        payload_b64 = base64.standard_b64encode(stream_payload.payloadData)
        return packet_header.seqId, stream_payload.command, payload_b64

    def encode(self, key_n: int, command: str, payload, subBiz: [str, None] = None):
        self.seqId += 1
        # ####################   UpstreamPayload    ################# #
        upstream_payload = UpstreamPayload_pb2.UpstreamPayload()
        upstream_payload.command = command
        upstream_payload.seqId = self.seqId
        if hasattr(payload, "DESCRIPTOR"):  # protos_class has attr "DESCRIPTOR"
            upstream_payload.payloadData = payload.SerializeToString()
        elif isinstance(payload, bytes):
            upstream_payload.payloadData = payload
        if isinstance(subBiz, (str, bytes)):
            upstream_payload.subBiz = subBiz
        payload_body = upstream_payload.SerializeToString()
        # ####################      Encoding        ################# #
        token_info = PacketHeader_pb2.TokenInfo__pb2.TokenInfo()
        token_info.tokenType = 1
        if self.config.acer.is_logined:
            token_info.token = self.config.api_st
        else:
            token_info.token = self.config.visitor_st
        header = PacketHeader_pb2.PacketHeader()
        header.appId = self.config.appId
        header.uid = self.config.userId
        header.instanceId = self.config.instanceId
        payload_len = len(payload_body)
        encrypted = payload_body
        if key_n in [1, 2]:
            key = self.config.ssecurity if key_n == 1 else self.config.sessKey
            encrypted = self._aes_encrypt(key, payload_body)
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

    def BasicRegister_Request(self):
        payload = RegisterRequest_pb2.RegisterRequest()
        app_info = RegisterRequest_pb2.AppInfo__pb2.AppInfo()
        app_info.sdkVersion = "kwai-acfun-live-link"
        app_info.linkVersion = "2.13.8"
        payload.appInfo.CopyFrom(app_info)
        device_info = RegisterRequest_pb2.DeviceInfo__pb2.DeviceInfo()
        device_info.platformType = 9
        device_info.deviceModel = "h5"
        if self.config.acer.is_logined:
            device_info.deviceId = self.config.did
        payload.deviceInfo.CopyFrom(device_info)
        payload.presenceStatus = 1
        payload.appActiveStatus = 1
        ztcommon_info = RegisterRequest_pb2.ZtCommonInfo__pb2.ZtCommonInfo()
        ztcommon_info.kpn = "ACFUN_APP"
        ztcommon_info.kpf = "PC_WEB"
        ztcommon_info.uid = int(self.config.userId)
        if self.config.acer.is_logined:
            ztcommon_info.did = self.config.did
        payload.instanceId = self.config.instanceId
        payload.ztCommonInfo.CopyFrom(ztcommon_info)
        return self.encode(1, "Basic.Register", payload, "mainApp")

    def ClientConfigGet_Request(self):
        payload = ClientConfigGetRequest_pb2.ClientConfigGetRequest()
        payload.version = 0
        return self.encode(2, "Basic.ClientConfigGet", payload)

    def KeepAlive_Request(self):
        payload = KeepAliveRequest_pb2.KeepAliveRequest()
        payload.presenceStatus = 1
        payload.appActiveStatus = 1
        payload.keepaliveIntervalSec = 120
        return self.encode(2, "Basic.KeepAlive", payload)

    def BasicPing_Request(self):
        return self.encode(2, "Basic.Ping", bytes())

    def MessageSession_Request(self):
        return self.encode(2, "Message.Session", bytes([16, 0]))

    def SessionCreate_Request(self, target_uid: int):
        payload = SessionCreateRequest_pb2.SessionCreateRequest()
        chat = SessionCreateRequest_pb2.ChatTarget__pb2.ChatTarget()
        chat.targetId = f"{target_uid}"
        chat.targetType = 0
        payload.chatTarget.CopyFrom(chat)
        return self.encode(2, "Session.Create", payload)

    def SessionRemove_Request(self, target_uid: int):
        payload = SessionRemoveRequest_pb2.SessionRemoveRequest()
        payload.targetId = target_uid
        payload.strTargetId = f"{target_uid}"
        return self.encode(2, "Message.SessionRemove", payload)

    def UserGroupList_Request(self):
        payload = GroupMemberListGetRequest_pb2.GroupMemberListGetRequest()
        payload.groupId = b"0"
        sync_cookie_payload = GroupMemberListGetRequest_pb2.SyncCookie__pb2.SyncCookie()
        sync_cookie_payload.syncOffset = -1
        payload.syncCookie.CopyFrom(sync_cookie_payload)
        return self.encode(2, "Group.UserGroupList", payload)

    def MessagePullOld_Request(self, uid: int, minSeq: int, maxSeq: int, count: int = 10):
        payload = PullOldRequest_pb2.PullOldRequest()
        payload.target.ParseFromString(proto_user_serialize(uid))
        payload.minSeq = minSeq
        payload.maxSeq = maxSeq
        payload.count = count
        return self.encode(2, "Message.PullOld", payload)

    def Message_Request(self, target_uid: int, content: bytes, content_type: int = 0):
        payload = Message_pb2.Message()
        # payload.seqId = int(f"{time.time():.0f}{1:0>6}")
        payload.clientSeqId = int(f"{time.time():.0f}{1:0>6}")
        payload.timestampMs = int(f"{time.time():.0f}{1:0>3}")
        payload.fromUser.ParseFromString(proto_user_serialize(self.config.userId))
        payload.targetId = target_uid
        payload.toUser.ParseFromString(proto_user_serialize(target_uid))
        payload.contentType = content_type
        payload.content = content
        payload.strTargetId = str(target_uid)
        return self.encode(2, "Message.Send", payload)

    def MessageContent_Request(self, target_uid: int, content: str):
        byte_content = message_content_serialize(content)
        return self.Message_Request(target_uid, byte_content, 0)

    def MessageImage_Request(self, target_uid: int, image_data: bytes):
        uploader_resp = acim_image_uploader(
            client=self.acws.config.acer.client,
            api_st=self.config.api_st.decode(),
            to_uid=f"{target_uid}",
            image_data=image_data
        )
        ks_uri = uploader_resp.get('uri')
        if ks_uri is None:
            print(uploader_resp)
            raise ValueError(uploader_resp['error_msg'])
        img_payload = Image_pb2.Image()
        img_payload.uri = ks_uri
        img_payload.width = 300
        img_payload.height = 300
        img_payload.contentLength = len(image_data)
        byte_content = img_payload.SerializeToString()
        return self.Message_Request(target_uid, byte_content, 1)
