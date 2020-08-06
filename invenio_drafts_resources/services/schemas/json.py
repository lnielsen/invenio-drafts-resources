# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marshmallow JSON schema."""


from invenio_records_resources.schemas.fields import SanitizedUnicode
from marshmallow import INCLUDE, Schema, fields


class DraftMetadataSchemaJSONV1(Schema):
    """Basic metadata schema class."""

    class Meta:
        """Meta class to accept unknwon fields."""

        unknown = INCLUDE

    _created_by = fields.Integer(required=True)


class DraftSchemaJSONV1(Schema):
    """Schema for drafts v1 in JSON."""

    id = fields.String(attribute="pid.pid_value")
    conceptrecid = SanitizedUnicode(
        attribute='metadata.conceptrecid',
        dump_only=True
    )
    metadata = fields.Nested(DraftMetadataSchemaJSONV1)
    links = fields.Raw()
    created = fields.Str()
    updated = fields.Str()
    status = fields.Str()
    expiry_date = fields.Str()
