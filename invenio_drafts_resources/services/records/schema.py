# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Record schema."""

from invenio_records_resources.services.records.schema import \
    RecordSchema as RecordSchemaBase
from marshmallow import fields


class RecordSchema(RecordSchemaBase):
    """Schema for records v1 in JSON."""

    conceptid = fields.Str()
