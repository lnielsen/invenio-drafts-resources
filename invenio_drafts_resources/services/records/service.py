# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""RecordDraft Service API."""

from elasticsearch_dsl.query import Q
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
    # Inherits record search, read, create, delete and update
    def search_drafts(self, identity, params=None, links_config=None,
                      es_preference=None, **kwargs):
        """Search for drafts records matching the querystring."""
        self.require_permission(identity, 'search_drafts')

        # Prepare and execute the search
        params = params or {}

        search_result = self._search(
            'search_drafts',
            identity,
            params,
            es_preference,
            record_cls=self.draft_cls,
            # `has_draft` systemfield is not defined here. This is not ideal
            # but it helps avoid overriding the method. See how is used in
            # https://github.com/inveniosoftware/invenio-rdm-records
            extra_filter=Q('term', has_draft=False),
            permission_action='read_draft',
            **kwargs
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_config=links_config
        )

    def read_draft(self, id_, identity, links_config=None):
        """Retrieve a draft."""
        # Resolve and require permission
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

        # Reindex the record to trigger update of computed values in the
        # available dumpers of the record.
        self.indexer.index(record)

        return self.result_item(
            self, identity, draft, links_config=links_config)

    def publish(self, id_, identity, links_config=None):
        """Publish a draft.

        Idea:
            - Get the draft from the data layer (draft is not passed in)
            - Validate it more strictly than when it was originally saved
              (drafts can be incomplete but only complete drafts can be turned
              into records)
            - Create or update associated (published) record with data

        NOTE: This process of taking data from the database and validating it
              back is tricky because there are a number of
              data representations and transformations. There can be mistakes
              within it as of writing. Don't take this flow as gospel yet.
        """
        self.require_permission(identity, "publish")

        # Get data layer draft
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        # Convert to service layer draft result item
        draft_item = self.result_item(
            self, identity, draft, links_config=None  # no need for links
        )
        # Convert to data projection i.e. draft result item's dict form. Since
        # there are no "errors" bc projection is taken directly from
        # DB, we can use draft_item.data. This dict form is what is
        # serialized out/deserialized in so it "should" be valid input to load.
        draft_data = draft_item.data

        # Purely used for validation purposes although we may actually want to
        # use it...
        data, _ = self.schema.load(
            identity,
            data=draft_data,
            pid=draft.pid,
            record=draft,
            raise_errors=True  # this is the default, but might as well be
                               # explicit
        )

        # Create or update published record
        record = self.record_cls.create_or_update_from(draft)

        # Run components
        for component in self.components:
            if hasattr(component, 'publish'):
                component.publish(draft=draft, record=record)

        record.commit()
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
            {},
            conceptpid=record.conceptpid,
            # TODO: Need to check if below line is correct?
            fork_version_id=record.revision_id,
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

        # Get published record if exists
        try:
            record = self.record_cls.get_record(draft.id)
        except NoResultFound:
            record = None

        # We soft-delete a draft when a published record exists, in order to
        # keep the version_id counter around for optimistic concurrency
        # control (both for ES indexing and for REST API clients)
        force = False if record else True

        # Run components
        for component in self.components:
            if hasattr(component, 'delete_draft'):
                component.delete_draft(
                    identity, draft=draft, record=record, force=force)

        draft.delete(force=force)
        db.session.commit()
        self.indexer.delete(draft, refresh=True)

        # Reindex the record to trigger update of computed values in the
        # available dumpers
        if record:
            self.indexer.index(record, arguments={"refresh": True})

        return True
