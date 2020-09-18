"""Example of a record model."""

from invenio_db import db
from invenio_records.models import RecordMetadataBase

from invenio_drafts_resources.records import DraftMetadataBase


class DraftMetadata(db.Model, DraftMetadataBase):
    """Model for mock module metadata."""

    __tablename__ = 'draft_mock_metadata'


class RecordMetadata(db.Model, RecordMetadataBase):
    """Model for mock module metadata."""

    __tablename__ = 'record_mock_metadata'
