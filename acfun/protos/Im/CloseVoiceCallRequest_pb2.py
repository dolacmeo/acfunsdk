# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: CloseVoiceCallRequest.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import User_pb2 as User__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1b\x43loseVoiceCallRequest.proto\x12\x1e\x41\x63\x46unDanmu.Im.Cloud.Voice.Call\x1a\nUser.proto\"\xfc\x01\n\x15\x43loseVoiceCallRequest\x12\x0e\n\x06roomId\x18\x01 \x01(\t\x12Q\n\x06reason\x18\x02 \x01(\x0e\x32\x41.AcFunDanmu.Im.Cloud.Voice.Call.CloseVoiceCallRequest.CloseReason\x12+\n\x08nextHost\x18\x03 \x01(\x0b\x32\x19.AcFunDanmu.Im.Basic.User\"S\n\x0b\x43loseReason\x12\x0e\n\nCR_UNKNOWN\x10\x00\x12\n\n\x06NORMAL\x10\x01\x12\r\n\tCANCELLED\x10\x02\x12\x0b\n\x07TIMEOUT\x10\x03\x12\x0c\n\x08\x46INISHED\x10\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'CloseVoiceCallRequest_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CLOSEVOICECALLREQUEST._serialized_start=76
  _CLOSEVOICECALLREQUEST._serialized_end=328
  _CLOSEVOICECALLREQUEST_CLOSEREASON._serialized_start=245
  _CLOSEVOICECALLREQUEST_CLOSEREASON._serialized_end=328
# @@protoc_insertion_point(module_scope)
