# coding=utf-8
import random
import sys
sys.path.append("./acfun/protos/Im")
import base64
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import acfun.protos.Im.TokenInfo_pb2 as TokenInfo_pb2
import acfun.protos.Im.PacketHeader_pb2 as PacketHeader_pb2
import acfun.protos.Im.UpstreamPayload_pb2 as UpstreamPayload_pb2
import acfun.protos.Im.DownstreamPayload_pb2 as DownstreamPayload_pb2
import acfun.protos.Im.RegisterRequest_pb2 as Register_pb2
import acfun.protos.Im.RegisterResponse_pb2 as RegisterResponse_pb2
import acfun.protos.Im.ErrorMessage_pb2 as ErrorMessage_pb2
import acfun.protos.Im.KeepAliveRequest_pb2 as KeepAliveRequest_pb2
import acfun.protos.Im.KeepAliveResponse_pb2 as KeepAliveResponse_pb2

# AES Padding
# https://blog.csdn.net/qq_39727936/article/details/114494791


class AcProtos:
    seqId = 0
    header_offset = 12
    payload_offset = 16
    command_map = {
        "Basic.Register": 'Basic_Register_Response',
        "Basic.KeepAlive": 'Keep_Alive_Response'
    }

    def __init__(self, config):
        self.config = config
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

        # keep = KeepAliveRequest_pb2.KeepAliveRequest()
        # # keep = KeepAliveResponse_pb2.KeepAliveResponse()
        # keep.ParseFromString(decrypted_data)
        # print("#" * 40)
        # print(keep)
        # print("#" * 40)

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
        self.seqId = packet_header.seqId
        self.config.appId = packet_header.appId
        self.config.instanceId = packet_header.instanceId
        payload_data = message[self.header_offset + packet_header_len:]
        if packet_header.encryptionMode == 1:  # kEncryptionServiceToken
            decrypted_data = self._aes_decrypt(self.config.ssecurity, payload_data)
        elif packet_header.encryptionMode == 2:  # kEncryptionSessionKey
            decrypted_data = self._aes_decrypt(self.config.sessKey, payload_data)
        else:  # kEncryptionNone
            decrypted_data = payload_data
        decrypted_data = decrypted_data[:packet_header.decodedPayloadLen]
        # print(f"decrypted_data[{len(decrypted_data)}]: ", decrypted_data)
        upstream_payload = UpstreamPayload_pb2.UpstreamPayload()
        upstream_payload.ParseFromString(decrypted_data)
        print("#" * 40)
        print(f"Command: {upstream_payload.command}")
        print("#" * 40)
        command = upstream_payload.command
        func_name = self.command_map.get(command)
        assert func_name is not None
        getattr(self, func_name)(upstream_payload.payloadData)

    def encode(self, key_n: int, payload_bytes: bytes):
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
        return b"".join([
            bytes.fromhex("abcd0001"),
            len(header_payload).to_bytes(4, "big"),
            len(encrypted).to_bytes(4, "big"),
            header_payload,
            encrypted
        ])

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
        return self.encode(1, payload_body)

    def Basic_Register_Response(self, recv_payload: bytes):
        reg_resp = RegisterResponse_pb2.RegisterResponse()
        reg_resp.ParseFromString(recv_payload)
        # print(reg_resp)
        # print("=" * 40)
        self.config.sessKey = base64.standard_b64encode(reg_resp.sessKey)
        print(f"sessKey: {self.config.sessKey}")

    @property
    def ping_message(self):
        if self.config.sessKey is None:
            return ""
        return self.Keep_Alive_Request()

    def Keep_Alive_Request(self):
        self.seqId += 1
        payload = KeepAliveRequest_pb2.KeepAliveRequest()
        payload.presenceStatus = 1
        payload.appActiveStatus = 1
        # pushST = KeepAliveRequest_pb2.PushServiceToken__pb2.PushServiceToken()
        # pushST.pushType = 0
        # pushST.token = b""
        # pushST.isPassThrough = True
        # payload.pushServiceToken.CopyFrom(pushST)
        # payload.pushServiceTokenList.CopyFrom(pushST)
        payload.keepaliveIntervalSec = 120
        # payload.ipv6Available = False
        upstream_payload = UpstreamPayload_pb2.UpstreamPayload()
        upstream_payload.command = "Basic.KeepAlive"
        upstream_payload.seqId = self.seqId
        upstream_payload.payloadData = payload.SerializeToString()
        payload_body = upstream_payload.SerializeToString()
        return self.encode(2, payload_body)

    def Keep_Alive_Response(self, recv_payload: bytes):
        keep_alive_payload = KeepAliveResponse_pb2.KeepAliveResponse()
        keep_alive_payload.ParseFromString(recv_payload)
        print(keep_alive_payload)
        print("=" * 40)

    def Downstream(self, decrypt_data):
        payload = DownstreamPayload_pb2.DownstreamPayload()
        payload.FromString(decrypt_data)
        return payload

