# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Draft Models API."""

from datetime import datetime

from invenio_db import db
from invenio_records.models import RecordMetadataBase
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils.types import UUIDType


class ParentRecordMixin:
    """A mixin factory that add the foreign keys to the parent record.

    It is intended to be added to the "child" record class, e.g.:
    ``class MyRecord(RecordBase, ParentRecordMixin(MyRecordParentClass))``.
    """
    parent_record_model = None

    @declared_attr
    def parent_id(cls):
        return db.Column(UUIDType, db.ForeignKey(cls.parent_record_model.id))

    @declared_attr
    def parent(cls):
        return db.relationship(cls.parent_record_model)

    # TODO: Add parent_order
    # TODO: Should both records and drafts have an order?


class ParentRecordStateMixin:
    """Database model mixin to keep the state of the latest and next version.

    We keep this data outside the parent record itself, because we want to
    update it without impacting the parent record's version counter. The
    version counter in the parent record we use to determine if we have to
    reindex all record verions.

    Usage:

    .. code-block:: python

        class MyParentState(db.Model, ParentRecordState):
            parent_record_model = MyParentRecord
            draft_model = MyDraft
            record_model = MyRecord
    """

    parent_record_model = None
    record_model = None
    draft_model = None

    @declared_attr
    def parent_id(cls):
        """Parent record identifier."""
        return db.Column(
            UUIDType,
            db.ForeignKey(cls.parent_record_model.id),
            primary_key=True,
        )

    @declared_attr
    def latest_id(cls):
        """UUID of the latest published record/draft.

        Note, since a record and draft share the same UUID, the UUID can be
        used to get both the record or the draft. It's a foreign key to the
        record to ensure that the record exists (and thus is published).
        """
        return db.Column(
            UUIDType,
            db.ForeignKey(cls.record_model.id),
            nullable=True,
        )

    count = db.Column(db.Integer, nullable=False)
    # Keep the latest index

    current_index = db.Column(db.Integer, nullable=False)
    # Keep the latest index - just incrementing

    @declared_attr
    def next_draft_id(cls):
        """UUID of the draft for the next version (yet to be published)."""
        return db.Column(
            UUIDType,
            db.ForeignKey(cls.draft_model.id),
            nullable=True,
        )



class DraftMetadataBase(RecordMetadataBase):
    """Represent a base class for draft metadata."""

    fork_version_id = db.Column(db.Integer)
    """Version ID of the record."""

    expires_at = db.Column(
        db.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
        default=datetime.utcnow,
        nullable=True
    )
    """Specifies when the draft expires. If `NULL` the draft doesn't expire."""
