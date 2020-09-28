# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from .draft import DraftActionResource, DraftResource, DraftVersionResource
from .draft_config import DraftActionResourceConfig, DraftResourceConfig, \
    DraftVersionResourceConfig
from .userrecords import UserRecordsResource
from .userrecords_config import UserRecordsResourceConfig

__all__ = (
    "DraftActionResource",
    "DraftActionResourceConfig",
    "DraftResource",
    "DraftResourceConfig",
    "DraftVersionResource",
    "DrafVersiontResourceConfig",
    "UserRecordsResource",
    "UserRecordsResourceConfig",
)
