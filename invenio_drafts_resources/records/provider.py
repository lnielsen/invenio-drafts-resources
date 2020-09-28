# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""PID Provider for records and drafts."""

from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.recordid_v2 import \
    RecordIdProviderV2 as RecordIdProviderV2Base


class RecordIdProviderV2(RecordIdProviderV2Base):
    """Provider with changed default PID status for newly created PIDs."""

    default_status_with_obj = PIDStatus.NEW
