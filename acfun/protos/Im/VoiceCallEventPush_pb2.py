# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: VoiceCallEventPush.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import User_pb2 as User__pb2
import VoiceCallAcceptedEvent_pb2 as VoiceCallAcceptedEvent__pb2
import VoiceCallAlreadyProcessedEvent_pb2 as VoiceCallAlreadyProcessedEvent__pb2
import VoiceCallCancelledEvent_pb2 as VoiceCallCancelledEvent__pb2
import VoiceCallClosedEvent_pb2 as VoiceCallClosedEvent__pb2
import VoiceCallDetailUpdateEvent_pb2 as VoiceCallDetailUpdateEvent__pb2
import VoiceCallRejectedEvent_pb2 as VoiceCallRejectedEvent__pb2
import VoiceCallRequestEvent_pb2 as VoiceCallRequestEvent__pb2
import VoiceCallTimeoutEvent_pb2 as VoiceCallTimeoutEvent__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18VoiceCallEventPush.proto\x12\x1e\x41\x63\x46unDanmu.Im.Cloud.Voice.Call\x1a\nUser.proto\x1a\x1cVoiceCallAcceptedEvent.proto\x1a$VoiceCallAlreadyProcessedEvent.proto\x1a\x1dVoiceCallCancelledEvent.proto\x1a\x1aVoiceCallClosedEvent.proto\x1a VoiceCallDetailUpdateEvent.proto\x1a\x1cVoiceCallRejectedEvent.proto\x1a\x1bVoiceCallRequestEvent.proto\x1a\x1bVoiceCallTimeoutEvent.proto\"\xfd\x05\n\x12VoiceCallEventPush\x12M\n\x0crequestEvent\x18\x14 \x01(\x0b\x32\x35.AcFunDanmu.Im.Cloud.Voice.Call.VoiceCallRequestEventH\x00\x12O\n\racceptedEvent\x18\x15 \x01(\x0b\x32\x36.AcFunDanmu.Im.Cloud.Voice.Call.VoiceCallAcceptedEventH\x00\x12O\n\rrejectedEvent\x18\x16 \x01(\x0b\x32\x36.AcFunDanmu.Im.Cloud.Voice.Call.VoiceCallRejectedEventH\x00\x12K\n\x0b\x63losedEvent\x18\x17 \x01(\x0b\x32\x34.AcFunDanmu.Im.Cloud.Voice.Call.VoiceCallClosedEventH\x00\x12Q\n\x0e\x63\x61ncelledEvent\x18\x18 \x01(\x0b\x32\x37.AcFunDanmu.Im.Cloud.Voice.Call.VoiceCallCancelledEventH\x00\x12_\n\x15\x61lreadyProcessedEvent\x18\x19 \x01(\x0b\x32>.AcFunDanmu.Im.Cloud.Voice.Call.VoiceCallAlreadyProcessedEventH\x00\x12M\n\x0ctimeoutEvent\x18\x1a \x01(\x0b\x32\x35.AcFunDanmu.Im.Cloud.Voice.Call.VoiceCallTimeoutEventH\x00\x12W\n\x11\x64\x65tailUpdateEvent\x18\x1b \x01(\x0b\x32:.AcFunDanmu.Im.Cloud.Voice.Call.VoiceCallDetailUpdateEventH\x00\x12\x0e\n\x06roomId\x18\x01 \x01(\t\x12+\n\x08operator\x18\x02 \x01(\x0b\x32\x19.AcFunDanmu.Im.Basic.UserB\x10\n\x0evoiceCallEventb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'VoiceCallEventPush_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _VOICECALLEVENTPUSH._serialized_start=322
  _VOICECALLEVENTPUSH._serialized_end=1087
# @@protoc_insertion_point(module_scope)
