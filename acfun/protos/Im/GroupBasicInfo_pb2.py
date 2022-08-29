# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: GroupBasicInfo.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import ForbiddenState_pb2 as ForbiddenState__pb2
import GroupLabel_pb2 as GroupLabel__pb2
import GroupStatus_pb2 as GroupStatus__pb2
import GroupType_pb2 as GroupType__pb2
import InvitePermissionType_pb2 as InvitePermissionType__pb2
import JoinNeedPermissionType_pb2 as JoinNeedPermissionType__pb2
import Location_pb2 as Location__pb2
import MultiForbiddenState_pb2 as MultiForbiddenState__pb2
import User_pb2 as User__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14GroupBasicInfo.proto\x12\x1b\x41\x63\x46unDanmu.Im.Cloud.Message\x1a\x14\x46orbiddenState.proto\x1a\x10GroupLabel.proto\x1a\x11GroupStatus.proto\x1a\x0fGroupType.proto\x1a\x1aInvitePermissionType.proto\x1a\x1cJoinNeedPermissionType.proto\x1a\x0eLocation.proto\x1a\x19MultiForbiddenState.proto\x1a\nUser.proto\"\xc4\t\n\x0eGroupBasicInfo\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x11\n\tgroupName\x18\x02 \x01(\t\x12(\n\x05\x61\x64min\x18\x03 \x01(\x0b\x32\x19.AcFunDanmu.Im.Basic.User\x12=\n\x0bgroupStatus\x18\x04 \x01(\x0e\x32(.AcFunDanmu.Im.Cloud.Message.GroupStatus\x12\x13\n\x0b\x64\x65scription\x18\x05 \x01(\t\x12O\n\x12joinNeedPermission\x18\x06 \x01(\x0e\x32\x33.AcFunDanmu.Im.Cloud.Message.JoinNeedPermissionType\x12\x12\n\ncreateTime\x18\x07 \x01(\x03\x12\x12\n\nupdateTime\x18\x08 \x01(\x03\x12\x39\n\tgroupType\x18\t \x01(\x0e\x32&.AcFunDanmu.Im.Cloud.Message.GroupType\x12\x43\n\x0e\x66orbiddenState\x18\n \x01(\x0e\x32+.AcFunDanmu.Im.Cloud.Message.ForbiddenState\x12O\n\x14invitePermissionType\x18\x0b \x01(\x0e\x32\x31.AcFunDanmu.Im.Cloud.Message.InvitePermissionType\x12\x12\n\nbizDefCode\x18\x0c \x01(\x05\x12\x18\n\x10\x64\x65\x66\x61ultGroupName\x18\r \x01(\t\x12\r\n\x05\x65xtra\x18\x0e \x01(\t\x12\x11\n\tisMuteAll\x18\x0f \x01(\x08\x12#\n\x1bonlyAdminUpdateGroupSetting\x18\x10 \x01(\x08\x12\x1a\n\x12onlyAdminRemindAll\x18\x11 \x01(\x08\x12/\n\x0cusersCanTalk\x18\x12 \x03(\x0b\x32\x19.AcFunDanmu.Im.Basic.User\x12\x33\n\x10usersKeepSilence\x18\x13 \x03(\x0b\x32\x19.AcFunDanmu.Im.Basic.User\x12\x14\n\x0cgroupHeadUrl\x18\x14 \x01(\t\x12\x37\n\x08location\x18\x15 \x01(\x0b\x32%.AcFunDanmu.Im.Cloud.Message.Location\x12\x0b\n\x03tag\x18\x16 \x01(\t\x12\x13\n\x0bgroupNumber\x18\x17 \x01(\t\x12\x14\n\x0cintroduction\x18\x18 \x01(\t\x12\x16\n\x0emaxMemberCount\x18\x19 \x01(\x05\x12M\n\x13multiForbiddenState\x18\x1a \x03(\x0e\x32\x30.AcFunDanmu.Im.Cloud.Message.MultiForbiddenState\x12\x17\n\x0fmaxManagerCount\x18\x1b \x01(\x05\x12\x36\n\x05label\x18\x1c \x03(\x0b\x32\'.AcFunDanmu.Im.Cloud.Message.GroupLabel\x12\x19\n\x11groupExtraSetting\x18\x1d \x01(\x03\x12 \n\x18groupInviteNeedUserAgree\x18\x1e \x01(\x08\x12\x1e\n\x16historyMessagesVisible\x18\x1f \x01(\x08\x12\x1a\n\x12groupDismissBanned\x18  \x01(\x08\x12\x17\n\x0fgroupQuitBanned\x18! \x01(\x08\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'GroupBasicInfo_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _GROUPBASICINFO._serialized_start=243
  _GROUPBASICINFO._serialized_end=1463
# @@protoc_insertion_point(module_scope)
