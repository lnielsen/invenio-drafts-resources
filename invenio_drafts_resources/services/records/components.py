# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Records service copmonent base classes."""

from invenio_records_resources.services.records.components import \
    MetadataComponent, ServiceComponent


class PIDComponent(ServiceComponent):
    """Service component for PID registraion."""

    def publish(self, draft=None, record=None):
        """Register persistent identifiers when publishing."""
        if not record.is_published:
            record.register()

    def delete_draft(self, identity, draft=None, record=None, force=False):
        """Unregister persistent identifiers for unpublished drafts."""
        if force:
            draft.__class__.pid.session_merge(draft)
            draft.pid.delete()
            draft.parent.__class__.pid.session_merge(draft.parent)
            draft.parent.pid.delete()


class DraftFilesComponent(ServiceComponent):
    """Draft files service component."""

    # TODO: Add tests for publishing a draft with files
    def publish(self, draft=None, record=None):
        """Copy bucket and files to record."""
        draft_files = draft.files
        bucket = draft_files.bucket
        if draft.files.enabled and bucket:
            # Set the draft bucket on the record also
            record.bucket = bucket
            record.bucket_id = bucket.id

            # Lock the bucket
            # TODO: Fix issues in REST API and UI for not allowing files to be
            # modified after editing a published record.
            # bucket.locked = True

            # TODO: actually "sync"
            # Copy over the files
            for key, df in draft_files.items():
                # TODO: Fix __setitem__ in FilesField, to support `None` for
                # metadata
                if df.metadata is not None:
                    record.files[key] = df.object_version, df.metadata
                else:
                    record.files[key] = df.object_version
        # TODO: Normally we don't need this... on record creation from a draft
        # with disabled files, the record should start with `enabled=False`.
        elif not draft.files.enabled:
            record.files.enabled = False

    def delete_draft(self, identity, draft=None, record=None, force=False):
        """Delete files associated with a draft if unpublished.

        :param force: If force is True, it means that the draft is being force
            deleted instead of soft deleted (i.e. an unpublished draft).
        """
        # If a draft is unpublished, we remove the associated files and bucket.
        # If a draft is published, we keep the files around until we expire the
        # draft.
        if force and draft.files.enabled:
            draft_files = draft.files
            bucket = draft_files.bucket
            # Collect keys to alter dict during the iteration.
            # TODO: Enhancement - add an API in the Files system field to
            # delete all something like draft.files.delete_all(force=True).
            keys = [file_key for file_key in draft.files]
            for file_key in keys:
                draft.files.delete(file_key)
            # Note: Bucket.remove() does not actually remove the data files
            # on disk. They have to be garbarge collected, since it's a
            # possibility that the physical file on disk is used linked in
            # other buckets
            draft.bucket = None
            draft.bucket_id = None
            bucket.remove()


class DraftMetadataComponent(MetadataComponent):
    """Service component for draft metadata integration."""

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Update draft metadata."""
        record.metadata = data.get('metadata', {})


class RelationsComponent(ServiceComponent):
    """Service component for PID relations integration."""

    # PIDNodeVersioning(pid=conceptrecid).insert_draft_child(child_pid=recid)
