# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: NoticeMessage.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import I18nCopyWriting_pb2 as I18nCopyWriting__pb2
import RichTextNoticeMessage_pb2 as RichTextNoticeMessage__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13NoticeMessage.proto\x12\x15\x41\x63\x46unDanmu.Im.Message\x1a\x15I18nCopyWriting.proto\x1a\x1bRichTextNoticeMessage.proto\"\xa1\x01\n\rNoticeMessage\x12\x44\n\x0erichTextNotice\x18\x02 \x01(\x0b\x32,.AcFunDanmu.Im.Message.RichTextNoticeMessage\x12\x0b\n\x03msg\x18\x05 \x01(\t\x12=\n\x0fi18nCopyWriting\x18\n \x01(\x0b\x32$.AcFunDanmu.Im.Basic.I18nCopyWritingb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'NoticeMessage_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _NOTICEMESSAGE._serialized_start=99
  _NOTICEMESSAGE._serialized_end=260
# @@protoc_insertion_point(module_scope)
