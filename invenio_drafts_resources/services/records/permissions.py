# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Drafts permissions."""

from invenio_records_permissions.generators import AnyUser
from invenio_records_permissions.policies.records import RecordPermissionPolicy


class RecordDraftPermissionPolicy(RecordPermissionPolicy):
    """Custom permission policy."""

    # FIXME: Revist this along the development
    # Default create should be "authenticated"?
    # TODO: Subclass records-resources policy and add *_draft actions
    can_create = [AnyUser()]
    can_publish = [AnyUser()]
    can_read_draft = [AnyUser()]
    can_update_draft = [AnyUser()]
    can_delete_draft = [AnyUser()]
