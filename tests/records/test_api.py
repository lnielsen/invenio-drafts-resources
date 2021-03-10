# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data access layer tests."""

import pytest
from invenio_search import current_search_client
from jsonschema import ValidationError
from mock_module.api import Draft, ParentRecord, Record
from sqlalchemy import inspect
from sqlalchemy.orm.exc import NoResultFound


#
# Create
#
def test_draft_create_empty(app, db):
    """Test draft creation."""
    # Empty draft creation works, and injects a schema.
    draft = Draft.create({})
    db.session.commit()
    assert draft.schema

    # JSONSchema validation works.
    pytest.raises(
        ValidationError,
        Draft.create,
        {'metadata': {'title': 1}}
    )


def test_draft_create_parent(app, db):
    """Test draft creation of the parent record."""
    draft = Draft.create({})
    db.session.commit()
    assert draft.schema.endswith('record-v1.0.0.json')
    assert draft.pid
    assert draft.parent.schema.endswith('parent-v1.0.0.json')
    assert draft.parent.pid

    assert draft.model.parent_id == draft.model.parent.id
    assert draft.pid.object_uuid != draft.parent.pid.object_uuid


#
# Create/Update from draft
#
def test_create_record_from_draft(app, db, example_draft):
    """Test create a record from a draft."""
    record = Record.create_from(example_draft)
    db.session.commit()
    assert example_draft.pid == record.pid
    assert example_draft.parent == record.parent


#
# Get
#
def test_draft_get_record(app, db, example_draft):
    """Test draft retrival."""
    draft = Draft.get_record(example_draft.id)
    # Test that the parent record is properly fetched.
    assert draft.parent == example_draft.parent


#
# Delete
#
def test_draft_force_delete(app, db, example_draft):
    """Test draft hard deletion."""
    parent_id = example_draft.parent.id
    example_draft.delete(force=True)
    db.session.commit()

    # Both parent and draft is deleted
    pytest.raises(NoResultFound, ParentRecord.get_record, parent_id)
    pytest.raises(NoResultFound, Draft.get_record, example_draft.id)


def test_draft_soft_delete(app, db, example_draft):
    """Test draft soft deletion."""
    parent_id = example_draft.parent.id
    example_draft.delete(force=False)
    db.session.commit()

    # Parent not deleted, but draft is soft deleted.
    assert ParentRecord.get_record(parent_id)
    pytest.raises(NoResultFound, Draft.get_record, example_draft.id)
    draft = Draft.get_record(example_draft.id, with_deleted=True)
    assert draft.parent.id == parent_id


def test_draft_undelete(app, db, example_draft):
    """Test undeleting a draft."""
    example_draft.delete()
    db.session.commit()

    draft = Draft.get_record(example_draft.id, with_deleted=True)
    assert draft.is_deleted
    draft.undelete()
    assert draft.parent.id == example_draft.parent.id


#
# Dumps/loads
#
def test_draft_dump_load_idempotence(app, db, example_draft):
    """Test idempotence of dumps/loads."""
    loaded_draft = Draft.loads(example_draft.dumps())
    assert example_draft == loaded_draft
    # Parent was dumped and loaded
    assert example_draft.parent == loaded_draft.parent
    # Test that SQLAlchemy model was loaded from the JSON and not DB.
    assert not inspect(loaded_draft.parent.model).persistent


#
# Indexing
#
def test_draft_indexing(app, db, es, example_draft, indexer):
    """Test indexing of a draft."""
    # Index document in ES
    assert indexer.index(example_draft)['result'] == 'created'

    # Retrieve document from ES
    data = current_search_client.get(
        'draftsresources-drafts-draft-v1.0.0',
        id=example_draft.id,
        doc_type='_doc'
    )

    # Loads the ES data and compare
    draft = Draft.loads(data['_source'])
    assert draft == example_draft
    assert draft.id == example_draft.id
    assert draft.revision_id == example_draft.revision_id
    assert draft.created == example_draft.created
    assert draft.updated == example_draft.updated
    assert draft.expires_at == example_draft.expires_at
    assert draft.parent == example_draft.parent

    # Check system fields
    draft.metadata == example_draft['metadata']


def test_draft_delete_reindex(app, db, es, example_draft, indexer):
    """Test reindexing of a soft-deleted draft."""
    draft = example_draft

    # Index draft
    assert indexer.index(draft)['result'] == 'created'

    # Delete record.
    draft.delete()
    db.session.commit()
    assert indexer.delete(draft)['result'] == 'deleted'

    # Update draft and reindex (this will cause troubles unless proper
    # optimistic concurrency control is used).
    draft.undelete()
    draft.commit()
    db.session.commit()
    assert indexer.index(draft)['result'] == 'created'
