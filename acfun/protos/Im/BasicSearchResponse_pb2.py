# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: BasicSearchResponse.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import GroupSearchResult_pb2 as GroupSearchResult__pb2
import UserSearchResult_pb2 as UserSearchResult__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19\x42\x61sicSearchResponse.proto\x12\x1a\x41\x63\x46unDanmu.Im.Cloud.Search\x1a\x17GroupSearchResult.proto\x1a\x16UserSearchResult.proto\"\x9b\x01\n\x13\x42\x61sicSearchResponse\x12@\n\nuserResult\x18\x01 \x03(\x0b\x32,.AcFunDanmu.Im.Cloud.Search.UserSearchResult\x12\x42\n\x0bgroupResult\x18\x02 \x03(\x0b\x32-.AcFunDanmu.Im.Cloud.Search.GroupSearchResultb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'BasicSearchResponse_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _BASICSEARCHRESPONSE._serialized_start=107
  _BASICSEARCHRESPONSE._serialized_end=262
# @@protoc_insertion_point(module_scope)
