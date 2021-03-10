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
def example_draft(db, input_data):
    """Example draft."""
    draft = Draft.create(
        input_data,
        expires_at=datetime(2020, 9, 7, 0, 0)
    )
    draft.commit()
    db.session.commit()
    return draft


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=Draft, record_to_index=lambda r: (r.index._name, '_doc')
    )
