# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: CommonStateSignalAuthorChatReady.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import AuthorChatPlayerInfo_pb2 as AuthorChatPlayerInfo__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n&CommonStateSignalAuthorChatReady.proto\x12\nAcFunDanmu\x1a\x1a\x41uthorChatPlayerInfo.proto\"\xae\x01\n CommonStateSignalAuthorChatReady\x12\x14\n\x0c\x61uthorChatId\x18\x01 \x01(\t\x12\x39\n\x0finviterUserInfo\x18\x02 \x01(\x0b\x32 .AcFunDanmu.AuthorChatPlayerInfo\x12\x39\n\x0finviteeUserInfo\x18\x03 \x01(\x0b\x32 .AcFunDanmu.AuthorChatPlayerInfob\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'CommonStateSignalAuthorChatReady_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _COMMONSTATESIGNALAUTHORCHATREADY._serialized_start=83
  _COMMONSTATESIGNALAUTHORCHATREADY._serialized_end=257
# @@protoc_insertion_point(module_scope)