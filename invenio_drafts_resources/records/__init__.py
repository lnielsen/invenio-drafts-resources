# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Drafts data access layer API."""

from .api import Draft, Record
from .models import DraftMetadataBase

__all__ = (
    "Draft",
    "DraftMetadataBase",
    "Record",
)
