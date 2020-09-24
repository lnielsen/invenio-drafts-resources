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

__all__ = (
    "DraftResource",
    "DraftResourceConfig",
    "DraftActionResource",
    "DraftActionResourceConfig",
    "DraftVersionResource",
    "DrafVersiontResourceConfig",
)
