# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: schema.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cschema.proto\"\x19\n\x06UserID\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\"*\n\x04User\x12\x0f\n\x07user_id\x18\x01 \x01(\x05\x12\x11\n\tuser_name\x18\x02 \x01(\t\"%\n\rUsersResponse\x12\x14\n\x05users\x18\x01 \x03(\x0b\x32\x05.User\"\x0e\n\x0c\x45mptyMessage\" \n\x0eStatusResponse\x12\x0e\n\x06status\x18\x01 \x01(\x08\x32\x80\x01\n\x08\x44\x61tabase\x12!\n\x07PutUser\x12\x05.User\x1a\x0f.StatusResponse\x12&\n\nDeleteUser\x12\x07.UserID\x1a\x0f.StatusResponse\x12)\n\x08GetUsers\x12\r.EmptyMessage\x1a\x0e.UsersResponseb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'schema_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _USERID._serialized_start=16
  _USERID._serialized_end=41
  _USER._serialized_start=43
  _USER._serialized_end=85
  _USERSRESPONSE._serialized_start=87
  _USERSRESPONSE._serialized_end=124
  _EMPTYMESSAGE._serialized_start=126
  _EMPTYMESSAGE._serialized_end=140
  _STATUSRESPONSE._serialized_start=142
  _STATUSRESPONSE._serialized_end=174
  _DATABASE._serialized_start=177
  _DATABASE._serialized_end=305
# @@protoc_insertion_point(module_scope)
