"""Example of a permission policy."""

from invenio_records_permissions.generators import AnyUser

from invenio_drafts_resources.services.records.permissions import \
    RecordDraftPermissionPolicy


class PermissionPolicy(RecordDraftPermissionPolicy):
    """Mock permission policy. All actions allowed."""

    can_search = [AnyUser()]
    can_create = [AnyUser()]
    can_read = [AnyUser()]
    can_read_draft = [AnyUser()]
    can_update = [AnyUser()]
    can_update_draft = [AnyUser()]
    can_delete = [AnyUser()]
    can_delete_draft = [AnyUser()]
    can_publish = [AnyUser()]
    can_read_files = [AnyUser()]
    can_update_files = [AnyUser()]
