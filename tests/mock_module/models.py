"""Example of a record model."""

from invenio_db import db
from invenio_records.models import RecordMetadataBase

from invenio_drafts_resources.records import DraftMetadataBase, \
    ParentRecordMixin, ParentStateMixin


class ParentRecordMetadata(db.Model, RecordMetadataBase):
    """Model for mock module metadata."""

    __tablename__ = 'parent_mock_metadata'


class DraftMetadata(db.Model, DraftMetadataBase,
                    ParentRecordMixin(ParentRecordMetadata)):
    """Model for mock module metadata."""

    __tablename__ = 'draft_mock_metadata'


class RecordMetadata(db.Model, RecordMetadataBase,
                     ParentRecordMixin(ParentRecordMetadata)):
    """Model for mock module metadata."""

    __tablename__ = 'record_mock_metadata'


class ParentState(db.Model, ParentStateMixin):
    """Model for mock module for parent state."""

    parent_record_model = ParentRecordMetadata
    record_model = RecordMetadata
    draft_model = DraftMetadata
