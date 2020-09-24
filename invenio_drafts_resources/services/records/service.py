# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""RecordDraft Service API."""

import uuid

from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services import RecordService
from sqlalchemy.orm.exc import NoResultFound

from .config import RecordDraftServiceConfig


class RecordDraftService(RecordService):
    """Draft Service interface.

    This service provides an interface to business logic for
    published AND draft records. When creating a custom service
    for a specialized record (e.g. Authors), consider if you need
    draft functionality or not. If you do, inherit from this service;
    otherwise, inherit from the RecordService directly.

    This service includes versioning.
    """

    default_config = RecordDraftServiceConfig

    @property
    def indexer(self):
        """Factory for creating an indexer instance."""
        return self.config.indexer_cls(
            record_cls=self.config.record_cls,
            record_to_index=self.config.record_to_index
        )

    # Draft attrs
    @property
    def draft_cls(self):
        """Factory for creating a record class."""
        return self.config.draft_cls

    # High-level API
    # Inherits record read, search, create, delete and update

    def read_draft(self, id_, identity, links_config=None):
        """Retrieve a draft."""
        # Resolve and require permission
        # TODO must handle delete records and tombstone pages
        # TODO: Can we make in a similar fashion than "create"?
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "read_draft", record=draft)

        # Run components
        for component in self.components:
            if hasattr(component, 'read_draft'):
                component.read_draft(identity, draft=draft)

        return self.result_item(
            self, identity, draft, links_config=links_config)

    def update_draft(self, id_, identity, data, links_config=None,
                     revision_id=None):
        """Replace a draft."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        self.check_revision_id(draft, revision_id)

        # Permissions
        self.require_permission(identity, "update_draft", record=draft)
        data, _ = self.schema.load(
            identity, data, pid=draft.pid, record=draft)

        # Run components
        for component in self.components:
            if hasattr(component, 'update_draft'):
                component.update_draft(
                    identity, record=draft, data=data)

        # TODO: remove next two lines. (See also record-resources)
        draft.update(data)
        draft.clear_none()
        draft.commit()

        if self.indexer:
            # FIXME: This would double index. Need delete->index?
            self.indexer.index(draft)

        return self.result_item(
            self, identity, draft, links_config=links_config)

    def create(self, identity, data, links_config=None):
        """Create a draft for a new record.

        It does not eagerly create the associated record.
        """
        # FIXME: This won't work with partial validation
        return self._create(
           self.draft_cls, identity, data, links_config=links_config
        )

    def _patch_data(self, record, data):
        """Temporarily here until the merge strategy is set."""
        # TODO: Implement better update/merge strategy
        for key in data.keys():
            record[key] = data[key]

    def _edit_or_create(self, id_):
        """Edit or create a draft based on the pid."""
        try:  # Draft exists
            draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        except NoResultFound:  # New draft
            record = self.record_cls.pid.resolve(id_)  # Needs Record as getter
            draft = self.draft_cls.create(
                {}, id_=record.id, fork_version_id=record.revision_id,
                pid=record.pid, conceptpid=record.conceptpid
            )

            # FIXME: Is this enough to copy over the data?
            draft.update(**record)

        return draft

    def edit(self, id_, identity, links_config=None):
        """Create a new revision or a draft for an existing record.

        Note: Because of the workflow, this method does not accept data.
        :param id_: record PID value.
        """
        self.require_permission(identity, "create")
        # Get draft
        draft = self._edit_or_create(id_)

        # Run components
        for component in self.components:
            if hasattr(component, 'edit'):
                component.edit(identity, draft=draft)

        draft.commit()
        db.session.commit()  # Persist DB

        # NOTE: Second condition avoids re-indexing and existing draft
        if self.indexer and draft.pid.pid_value != id_:
            self.indexer.index(draft)

        return self.result_item(
            self, identity, draft, links_config=links_config)

    def publish(self, id_, identity, links_config=None):
        """Publish a draft."""
        self.require_permission(identity, "publish")
        # Get draft
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        # Fully validate draft now
        # TODO: Add error_map for `ValidationError` in the resource config
        # FIXME: Check partial vs absolute validation
        # data, _ = self.schema.load(identity, data=draft.dumps())

        record = self.record_cls.create_or_update_from(draft)

        # Run components
        for component in self.components:
            if hasattr(component, 'publish'):
                component.publish(draft=draft, record=record)

        # Register if needed
        if not record.is_published:
            record.register()

        record.commit()
        db.session.commit()

        # Remove draft. Hard delete to remove the uuid (pk) from the table.
        draft.delete(force=True)
        db.session.commit()  # Persist DB
        # Index the record
        if self.indexer:
            self.indexer.delete(draft)
            self.indexer.index(record)

        return self.result_item(
            self, identity, record, links_config=links_config)

    def new_version(self, id_, identity, links_config=None):
        """Create a new version of a record."""
        self.require_permission(identity, "create")
        # Get record
        record = self.record_cls.pid.resolve(id_)
        # Create new record (relation done by minter)

        draft = self.draft_cls.create(
            {"metadata": record.metadata},  # FIXME: This doesnt look good
            conceptpid=record.conceptpid,
            fork_version_id=record.revision_id
        )

        # Run components
        for component in self.components:
            if hasattr(component, 'new_version'):
                component.new_version(identity, draft=draft, record=record)

        draft.commit()
        db.session.commit()  # Persist DB

        # Index the record
        if self.indexer:
            self.indexer.index(draft)

        return self.result_item(
            self, identity, draft, links_config=links_config)

    def delete_draft(self, id_, identity, revision_id=None):
        """Delete a record from database and search indexes."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        self.check_revision_id(draft, revision_id)

        # Permissions
        self.require_permission(identity, "delete_draft", record=draft)

        # Run components
        for component in self.components:
            if hasattr(component, 'delete_draft'):
                component.delete(identity, record=draft)

        draft.delete()
        db.session.commit()

        if self.indexer:
            self.indexer.delete(draft)

        return True
