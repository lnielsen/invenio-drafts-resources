# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Draft Services."""

from .files import FileMetadataService, FileMetadataServiceConfig, \
    FileService, FileServiceConfig
from .records import RecordDraftService, RecordDraftServiceConfig

__all__ = (
    "FileMetadataService",
    "FileMetadataServiceConfig",
    "FileService",
    "FileServiceConfig",
    "RecordDraftService",
    "RecordDraftServiceConfig",
)
