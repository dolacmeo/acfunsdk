# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: GroupInviteRequest.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import User_pb2 as User__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18GroupInviteRequest.proto\x12\x1b\x41\x63\x46unDanmu.Im.Cloud.Message\x1a\nUser.proto\"\x86\x01\n\x12GroupInviteRequest\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12*\n\x07members\x18\x02 \x03(\x0b\x32\x19.AcFunDanmu.Im.Basic.User\x12\x13\n\x0b\x64\x65scContent\x18\x03 \x01(\t\x12\x1e\n\x16historyMessagesVisible\x18\x04 \x01(\x08\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'GroupInviteRequest_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _GROUPINVITEREQUEST._serialized_start=70
  _GROUPINVITEREQUEST._serialized_end=204
# @@protoc_insertion_point(module_scope)
