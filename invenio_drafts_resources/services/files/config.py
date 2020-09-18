# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""RecordDraft File Service API config."""

from invenio_records_resources.services import \
    FileMetadataServiceConfig as FileMetadataServiceConfigBase
from invenio_records_resources.services import \
    FileServiceConfig as FileServiceConfigBase


class FileServiceConfig(FileServiceConfigBase):
    """Draft File Service configuration."""

    pass


class FileMetadataServiceConfig(FileMetadataServiceConfigBase):
    """Draft File Metadata Service configuration."""

    # TODO: FILL ME!
    pass
