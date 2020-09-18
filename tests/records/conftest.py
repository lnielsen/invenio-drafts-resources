# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module tests."""

from datetime import datetime

import pytest
from invenio_indexer.api import RecordIndexer
from mock_module.api import Draft


@pytest.fixture()
def example_data():
    """Example data."""
    return {
        'metadata': {'title': 'Test'}
    }


@pytest.fixture()
def example_record(db, example_data):
    """Example record."""
    record = Draft.create(
        example_data,
        expires_at=datetime(2020, 9, 7, 0, 0)
    )
    db.session.commit()
    return record


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(record_cls=Draft)
