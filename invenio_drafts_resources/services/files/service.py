# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""RecordDraft File Service API."""


from invenio_records_resources.services import FileMetadataService, FileService

from .config import FileMetadataServiceConfig, FileServiceConfig


class FileService(FileService):
    """RecordDraft File Service."""

    # NOTE: We can just rely on Records-Resources FileService.
    # Only config is needed.
    default_config = FileServiceConfig


class FileMetadataService(FileMetadataService):
    """RecordDraft File Metadata Service."""

    # NOTE: We can just rely on Records-Resources FileService.
    # Only config is needed.
    default_config = FileMetadataServiceConfig
