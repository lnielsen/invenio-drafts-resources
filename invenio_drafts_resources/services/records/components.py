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


class DraftMetadataComponent(MetadataComponent):
    """Service component for draft metadata integration."""

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Update draft metadata."""
        record.metadata = data.get('metadata', {})


class RelationsComponent(ServiceComponent):
    """Service component for PID relations integration."""

    # PIDNodeVersioning(pid=conceptrecid).insert_draft_child(child_pid=recid)
