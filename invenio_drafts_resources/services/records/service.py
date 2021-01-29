# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""RecordDraft Service API."""

from invenio_db import db
from invenio_records_resources.services import RecordService
from sqlalchemy.orm.exc import NoResultFound

from .config import RecordDraftServiceConfig


class RecordDraftService(RecordService):
    """Draft Service interface.

    This service provides an interface to business logic for
    published AND draft records. When creating a custom service
    for a specialized record (e.g. authors), consider if you need
    draft functionality or not. If you do, inherit from this service;
    otherwise, inherit from the RecordService directly.

    This service includes versioning.
    """

    default_config = RecordDraftServiceConfig

    # Draft attrs
    @property
    def draft_cls(self):
        """Factory for creating a record class."""
        return self.config.draft_cls

    # High-level API
    # Inherits record read, create, delete and update
    def search(self, identity, params=None, links_config=None,
               es_preference=None, **kwargs):
        """Search for records matching the querystring."""
        params = params or {}
        params.update(kwargs)

        status = params.pop("status", "published")
        record_cls = self.draft_cls if status == "draft" else self.record_cls

        return super().search(
            identity,
            params=params,
            links_config=links_config,
            es_preference=es_preference,
            record_cls=record_cls,
            # we don't pass kwargs, because they have already been merged.
        )

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

        data, errors = self.schema.load(
            identity,
            data,
            pid=draft.pid,
            record=draft,
            # Saving a draft only saves valid metadata and reports
            # (doesn't raise) errors
            raise_errors=False
        )

        # Run components
        for component in self.components:
            if hasattr(component, 'update_draft'):
                component.update_draft(
                    identity, record=draft, data=data)

        # TODO: remove next two lines. (See also record-resources)
        draft.update(data)
        draft.clear_none()
        draft.commit()
        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_config=links_config,
            errors=errors
        )

    def create(self, identity, data, links_config=None):
        """Create a draft for a new record.

        It does NOT eagerly create the associated record.
        """
        return self._create(
           self.draft_cls,
           identity,
           data,
           links_config=links_config,
           raise_errors=False
        )

    def edit(self, id_, identity, links_config=None):
        """Create a new revision or a draft for an existing record.

        Note: Because of the workflow, this method does not accept data.
        :param id_: record PID value.
        """
        self.require_permission(identity, "create")
        # Draft exists - return it
        try:
            draft = self.draft_cls.pid.resolve(id_, registered_only=False)
            return self.result_item(
                self, identity, draft, links_config=links_config)
        except NoResultFound:
            pass

        # Draft does not exists - create a new draft or get a soft deleted
        # draft.
        record = self.record_cls.pid.resolve(id_)
        try:
            # We soft-delete a draft once it has been published, in order to
            # keep the version_id counter around for optimistic concurrency
            # control (both for ES indexing and for REST API clients)
            draft = self.draft_cls.get_record(record.id, with_deleted=True)
            if draft.is_deleted:
                draft.undelete()
                draft.update(**record)
                draft.pid = record.pid
                draft.conceptpid = record.conceptpid
                draft.fork_version_id = record.revision_id
        except NoResultFound:
            # If a draft was ever force deleted, then we will create the draft.
            # This is a very exceptional case as normally, when we edit a
            # record then the soft-deleted draft exists and we are in above
            # case.
            draft = self.draft_cls.create(
                record, id_=record.id, fork_version_id=record.revision_id,
                pid=record.pid, conceptpid=record.conceptpid
            )

        # Run components
        for component in self.components:
            if hasattr(component, 'edit'):
                component.edit(identity, draft=draft)

        draft.commit()
        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self, identity, draft, links_config=links_config)

    def publish(self, id_, identity, links_config=None):
        """Publish a draft."""
        self.require_permission(identity, "publish")

        # Get draft
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        data, _ = self.schema.load(
            identity,
            data=draft.dumps(),
            pid=draft.pid,
            record=draft,
            raise_errors=True  # this is the default, but might as well be
                               # explicit
        )

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

        draft.delete()
        db.session.commit()  # Persist DB
        self.indexer.delete(draft)
        self.indexer.index(record)

        return self.result_item(
            self, identity, record, links_config=links_config)

    def new_version(self, id_, identity, links_config=None):
        """Create a new version of a record."""
        self.require_permission(identity, "create")

        # Get record
        record = self.record_cls.pid.resolve(id_)

        # Create new record
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
        db.session.commit()
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

        try:
            record = self.record_cls.pid.resolve(id_, registered_only=False)
        except NoResultFound:  # FIXME: Should be at resolver level?
            record = None
        # If it is tight to a record soft remove, else wipe fully
        force = True if record else False
        draft.delete(force=force)
        db.session.commit()
        self.indexer.delete(draft)

        return True
