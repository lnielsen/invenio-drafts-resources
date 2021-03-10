# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Draft API."""

from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.systemfields import ModelField
from invenio_records_resources.records import Record as RecordBase
from invenio_records_resources.records.systemfields import PIDField, \
    PIDStatusCheckField
from sqlalchemy.orm.exc import NoResultFound


class DraftRecordIdProviderV2(RecordIdProviderV2):
    """Draft PID provider."""

    default_status_with_obj = PIDStatus.NEW


class ParentRecord(RecordBase):
    """Parent record API."""

    # Configuration
    model_cls = None

    pid = PIDField('id', provider=DraftRecordIdProviderV2, delete=True)


class Record(RecordBase):
    """Record base API.

    Note: This class is meant to work along a with a draft class.
    """

    # Configuration
    model_cls = None

    pid = PIDField('id', provider=DraftRecordIdProviderV2, delete=True)

    is_published = PIDStatusCheckField(status=PIDStatus.REGISTERED)

    #: List of field names (strings) to copy from the draft on create.
    create_from_draft = []

    #: List of field names (strings) to copy from the draft on update.
    update_from_draft = []

    # TODO: Below three methods create_from(), update_from() and register() has
    # to be refactored. They are accessing "parent" but it may not be defined.
    # Instead, this work should be delegated to the system fields, but it's not
    # easy to add a new pre/post_create_from pre/post_register hook.
    @classmethod
    def create_from(cls, draft):
        """Create a new record from a draft."""
        record = cls.create(
            {},
            id_=draft.id,
            pid=draft.pid,
            **{f: getattr(draft, f) for f in cls.create_from_draft}
        )

        # NOTE: Merge pid into the current db session if not already in the
        # session.
        cls.pid.session_merge(record)
        record.parent.__class__.pid.session_merge(record.parent)

        record.update_from(draft)

        return record

    def update_from(self, draft):
        """Update a record from a draft."""
        # Overwrite data
        self.update(**draft)
        for f in self.update_from_draft:
            setattr(self, f, getattr(draft, f))
        return self

    def register(self):
        """Register the persistent identifiers associated with the record."""
        if not self.parent.pid.is_registered():
            self.parent.pid.register()
            self.parent.commit()
        self.pid.register()


class Draft(Record):
    """Draft base API for metadata creation and manipulation."""

    # WHY: We want to force the model_cls to be specified by the user
    # No default one is given, only the base.
    model_cls = None

    pid = PIDField('id', provider=DraftRecordIdProviderV2, delete=False)

    expires_at = ModelField()

    fork_version_id = ModelField()
