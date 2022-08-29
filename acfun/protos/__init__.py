# coding=utf-8
import random
import sys
sys.path.append("./acfun/protos/Im")
import base64
from Crypto import Random
from Crypto.Cipher import AES
import acfun.protos.Im.TokenInfo_pb2 as TokenInfo_pb2
import acfun.protos.Im.PacketHeader_pb2 as PacketHeader_pb2
import acfun.protos.Im.UpstreamPayload_pb2 as UpstreamPayload_pb2
import acfun.protos.Im.DownstreamPayload_pb2 as DownstreamPayload_pb2
import acfun.protos.Im.RegisterRequest_pb2 as Register_pb2
import acfun.protos.Im.ErrorMessage_pb2 as ErrorMessage_pb2


class AcProtos:
    SeqId = 0
    header_offset = 12
    payload_offset = 16

    def __init__(self, config):
        self.config = config
        self.SeqId += 1
        pass

    def _aes_encrypt(self, key, payload):
        print("key: ", key)
        key = base64.standard_b64decode(key)
        iv = Random.new().read(AES.block_size)
        print("iv:", iv)
        p = len(payload) % AES.block_size
        if p != 0:
            pad_len = (AES.block_size - p)
            payload = payload + b'\x00'
            if pad_len > 1:
                payload = payload + b'\r' * (pad_len - 1)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        result = cipher.encrypt(payload)
        return iv + result

    def _aes_decrypt(self, key, data):
        key = base64.standard_b64decode(key)
        iv = data[:self.payload_offset]
        payload = data[self.payload_offset:]
        print(f"key: {key}")
        print(f"iv : {iv}")
        print(f"payload {len(payload)}: {payload}")
        cipher = AES.new(key, AES.MODE_CBC, iv)
        result = cipher.decrypt(payload)
        return result

    def receive(self, message: bytes):
        # print(f"total length: {len(message)}")
        packet_header_len = int.from_bytes(message[4:8], byteorder='big')
        payload_len = int.from_bytes(message[8:12], byteorder='big')
        # print(f"packet_header_len: {packet_header_len} {str(message[4:8])}")
        # print(f"payload_len: {payload_len} {str(message[8:12])}")
        packet_header = PacketHeader_pb2.PacketHeader()
        header = message[self.header_offset:self.header_offset + packet_header_len]
        packet_header.ParseFromString(header)
        # print(packet_header)
        # print("=" * 40)
        if packet_header.decodedPayloadLen == 17:
            print("recv error: ", base64.standard_b64encode(message[self.header_offset + packet_header_len:]))
            return
        payload_data = message[self.header_offset + packet_header_len:]
        # print(f"payload: {payload_data}")
        key = self.config.ssecurity if self.config.acer.is_logined else self.config.acSecurity
        # print(f"encryptionMode: {packet_header.kEncryptionServiceToken}")
        print(f"{len(payload_data)} {payload_data}")
        if packet_header.encryptionMode == 0:  # kEncryptionServiceToken
            decode_data = payload_data[self.payload_offset:]
        else:
            decode_data = self._aes_decrypt(key, payload_data)
        print(len(decode_data), decode_data)
        upstream_payload = UpstreamPayload_pb2.UpstreamPayload()
        upstream_payload.ParseFromString(decode_data[:packet_header.decodedPayloadLen])
        print(upstream_payload)
        print("=" * 40)
        reg = Register_pb2.RegisterRequest()
        reg.ParseFromString(upstream_payload.payloadData)
        print(reg)
        print("=" * 40)
        # payload = self.Downstream(decode_data)
        # print(payload)
        # reg = Register_pb2.RegisterResponse()
        # reg.ParseFromString(upstream_payload.payloadData)
        # print(reg)

    def PacketHeader(self, payload_len: int, encrypted_len: int):
        token_info = TokenInfo_pb2.TokenInfo()
        token_info.tokenType = 1
        if self.config.acer.is_logined:
            token_info.token = self.config.api_st
        else:
            token_info.token = self.config.visitor_st
        header = PacketHeader_pb2.PacketHeader()
        # header.appId = 13
        header.uid = self.config.userId
        # header.instanceId = 0
        header.decodedPayloadLen = payload_len
        header.encryptionMode = 1
        header.tokenInfo.CopyFrom(token_info)
        header.seqId = self.SeqId
        header.kpn = b"ACFUN_APP"
        header_payload = header.SerializeToString()
        return [
            bytes.fromhex("abcd0001"),
            len(header_payload).to_bytes(4, "big"),
            encrypted_len.to_bytes(4, "big"),
            header_payload
        ]

    def Downstream(self, decrypt_data):
        payload = DownstreamPayload_pb2.DownstreamPayload()
        payload.FromString(decrypt_data)
        return payload

    def Basic_Register(self):
        # reg = Register_pb2.RegisterRequest()
        # reg_resp = Register_pb2.RegisterResponse()
        payload = Register_pb2.RegisterRequest()
        app_info = Register_pb2.AppInfo__pb2.AppInfo()
        app_info.sdkVersion = "2.13.11-rc.2"
        app_info.linkVersion = "2.13.8"
        payload.appInfo.CopyFrom(app_info)
        device_info = Register_pb2.DeviceInfo__pb2.DeviceInfo()
        device_info.platformType = 9
        device_info.deviceModel = "h5"
        device_info.deviceId = self.config.did
        payload.deviceInfo.CopyFrom(device_info)
        payload.presenceStatus = 1
        payload.appActiveStatus = 1
        ztcommon_info = Register_pb2.ZtCommonInfo__pb2.ZtCommonInfo()
        ztcommon_info.kpn = b"ACFUN_APP"
        ztcommon_info.kpf = b"PC_WEB"
        ztcommon_info.uid = int(self.config.userId)
        ztcommon_info.did = self.config.did
        payload.ztCommonInfo.CopyFrom(ztcommon_info)
        upstream_payload = UpstreamPayload_pb2.UpstreamPayload()
        upstream_payload.command = "Basic.Register"
        upstream_payload.seqId = self.SeqId
        upstream_payload.retryCount = 1
        upstream_payload.payloadData = payload.SerializeToString()
        payload_body = upstream_payload.SerializeToString()
        key = self.config.ssecurity if self.config.acer.is_logined else self.config.acSecurity
        # print(f"key: {key}", len(payload_body))
        encrypted = self._aes_encrypt(key, payload_body)
        data = self.PacketHeader(len(payload_body), len(encrypted))
        data.append(encrypted)
        return b"".join(data)

