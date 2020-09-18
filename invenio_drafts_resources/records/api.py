# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Draft API."""

from invenio_db import db
from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.systemfields import ModelField
from invenio_records_resources.records import Record as RecordBase
from invenio_records_resources.records.systemfields import PIDField, \
    PIDStatusCheckField
from sqlalchemy.orm.exc import NoResultFound

RecordIdProviderV2.default_status_with_obj = PIDStatus.NEW


class Record(RecordBase):
    """Record base API.

    Note: This class is meant to work along a with a draft class.
    """

    # Configuration
    model_cls = None

    pid = PIDField('id', provider=RecordIdProviderV2)

    conceptpid = PIDField('conceptid', provider=RecordIdProviderV2)

    is_published = PIDStatusCheckField(status=PIDStatus.REGISTERED)

    @classmethod
    def create_or_update_from(cls, draft):
        """Create of update the record based on the draft content."""
        try:  # New version
            record = cls.get_record(draft.id)
        except NoResultFound:  # New revision
            record = cls.create(
                {}, id_=draft.id, pid=draft.pid, conceptpid=draft.conceptpid)

        # NOTE: Make session consistent. See PIDField docs for more info.
        cls.pid.session_merge(record)
        cls.conceptpid.session_merge(record)
        # Overwrite data
        # FIXME: Data validation should be done one step up self.schema access
        record.update(**draft)

        return record

    def register(self):
        """Register the conceptrecid."""
        # FIXME: Why does dump not call str on this?
        register_str = str(PIDStatus.REGISTERED)
        if not self.conceptpid.is_registered():
            if self.conceptpid.register():
                self["conceptpid"]["status"] = register_str

        if self.pid.register():
            self["conceptpid"]["status"] = register_str


class Draft(Record):
    """Draft base API for metadata creation and manipulation."""

    # WHY: We want to force the model_cls to be specified by the user
    # No default one is given, only the base.
    model_cls = None

    pid = PIDField('id', provider=RecordIdProviderV2, delete=False)

    conceptpid = PIDField(
        'conceptid', provider=RecordIdProviderV2,  delete=False)

    expires_at = ModelField()

    fork_version_id = ModelField()
