# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: SessionFolderSyncResponse.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import SessionFolderBasic_pb2 as SessionFolderBasic__pb2
import SessionReferenceUpdateItem_pb2 as SessionReferenceUpdateItem__pb2
import SyncCookie_pb2 as SyncCookie__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fSessionFolderSyncResponse.proto\x12!AcFunDanmu.Im.Cloud.SessionFolder\x1a\x18SessionFolderBasic.proto\x1a SessionReferenceUpdateItem.proto\x1a\x10SyncCookie.proto\"\xef\x02\n\x19SessionFolderSyncResponse\x12\x33\n\nsyncCookie\x18\x01 \x01(\x0b\x32\x1f.AcFunDanmu.Im.Basic.SyncCookie\x12Q\n\x12sessionFolderBasic\x18\x02 \x03(\x0b\x32\x35.AcFunDanmu.Im.Cloud.SessionFolder.SessionFolderBasic\x12L\n\x05\x61\x64\x64\x65\x64\x18\x03 \x03(\x0b\x32=.AcFunDanmu.Im.Cloud.SessionFolder.SessionReferenceUpdateItem\x12N\n\x07removed\x18\x04 \x03(\x0b\x32=.AcFunDanmu.Im.Cloud.SessionFolder.SessionReferenceUpdateItem\x12\x14\n\x0cnotFullFetch\x18\x05 \x01(\x08\x12\x16\n\x0e\x63learLocalData\x18\x06 \x01(\x08\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'SessionFolderSyncResponse_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _SESSIONFOLDERSYNCRESPONSE._serialized_start=149
  _SESSIONFOLDERSYNCRESPONSE._serialized_end=516
# @@protoc_insertion_point(module_scope)
