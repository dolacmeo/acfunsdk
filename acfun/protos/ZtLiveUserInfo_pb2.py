# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ZtLiveUserInfo.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import ImageCdnNode_pb2 as ImageCdnNode__pb2
import ZtLiveUserIdentity_pb2 as ZtLiveUserIdentity__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14ZtLiveUserInfo.proto\x12\nAcFunDanmu\x1a\x12ImageCdnNode.proto\x1a\x18ZtLiveUserIdentity.proto\"\xa1\x01\n\x0eZtLiveUserInfo\x12\x0e\n\x06userId\x18\x01 \x01(\x03\x12\x10\n\x08nickname\x18\x02 \x01(\t\x12(\n\x06\x61vatar\x18\x03 \x03(\x0b\x32\x18.AcFunDanmu.ImageCdnNode\x12\r\n\x05\x62\x61\x64ge\x18\x04 \x01(\t\x12\x34\n\x0cuserIdentity\x18\x05 \x01(\x0b\x32\x1e.AcFunDanmu.ZtLiveUserIdentityb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ZtLiveUserInfo_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ZTLIVEUSERINFO._serialized_start=83
  _ZTLIVEUSERINFO._serialized_end=244
# @@protoc_insertion_point(module_scope)