# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: GroupJoinRequestGetResponse.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import GroupMember_pb2 as GroupMember__pb2
import JoinRequestStatus_pb2 as JoinRequestStatus__pb2
import User_pb2 as User__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n!GroupJoinRequestGetResponse.proto\x12\x1b\x41\x63\x46unDanmu.Im.Cloud.Message\x1a\x11GroupMember.proto\x1a\x17JoinRequestStatus.proto\x1a\nUser.proto\"\xc3\x02\n\x1bGroupJoinRequestGetResponse\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12*\n\x07inviter\x18\x02 \x01(\x0b\x32\x19.AcFunDanmu.Im.Basic.User\x12+\n\x08invitees\x18\x03 \x03(\x0b\x32\x19.AcFunDanmu.Im.Basic.User\x12\x0f\n\x07\x66indWay\x18\x04 \x01(\x05\x12\x13\n\x0b\x64\x65scContent\x18\x05 \x01(\t\x12>\n\x06status\x18\x06 \x01(\x0e\x32..AcFunDanmu.Im.Cloud.Message.JoinRequestStatus\x12T\n\x12inviteeMembersRole\x18\x07 \x01(\x0e\x32\x38.AcFunDanmu.Im.Cloud.Message.GroupMember.GroupMemberRoleb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'GroupJoinRequestGetResponse_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _GROUPJOINREQUESTGETRESPONSE._serialized_start=123
  _GROUPJOINREQUESTGETRESPONSE._serialized_end=446
# @@protoc_insertion_point(module_scope)
