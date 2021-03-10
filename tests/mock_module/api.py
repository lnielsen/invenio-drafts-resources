"""Example of a record draft API."""

from invenio_records.systemfields import ConstantField
from invenio_records_resources.records.systemfields import IndexField

from invenio_drafts_resources.records.api import Draft as DraftBase
from invenio_drafts_resources.records.api import \
    ParentRecord as ParentRecordBase
from invenio_drafts_resources.records.api import Record as RecordBase
from invenio_drafts_resources.records.systemfields import ParentField

from .models import DraftMetadata, ParentRecordMetadata, RecordMetadata


class ParentRecord(ParentRecordBase):
    """Example parent record."""

    # Configuration
    model_cls = ParentRecordMetadata

    # System fields
    schema = ConstantField(
        '$schema', 'http://localhost/schemas/records/parent-v1.0.0.json')


class Record(RecordBase):
    """Example record API."""

    # Configuration
    model_cls = RecordMetadata

    # System fields
    schema = ConstantField(
        '$schema', 'http://localhost/schemas/records/record-v1.0.0.json')

    index = IndexField(
        'draftsresources-records-record-v1.0.0',
        search_alias='draftsresources-records'
    )

    parent = ParentField(
        ParentRecord, create=False, soft_delete=False, hard_delete=False)

    create_from_draft = [
        'parent'
    ]


class Draft(DraftBase):
    """Example record API."""

    # Configuration
    model_cls = DraftMetadata

    # System fields
    schema = ConstantField(
        '$schema', 'http://localhost/schemas/records/record-v1.0.0.json')

    index = IndexField(
        'draftsresources-drafts-draft-v1.0.0',
        search_alias='draftsresources-drafts'
    )

    parent = ParentField(
        ParentRecord, create=True, soft_delete=False, hard_delete=True)
