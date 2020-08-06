# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Draft minter."""

from invenio_pidstore.minters import recid_minter_v2
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2


# Keep `record_uuid` to comply with minter interface
def conceptrecid_minter_v2(record_uuid=None, data=None):
    """Mint the Concept RECID, reserves it for the record."""
    conceptrecid = PersistentIdentifier.create(
        pid_type='recid',
        pid_value=str(RecordIdProviderV2.generate_id()),
        status=PIDStatus.RESERVED,
    )

    data['conceptrecid'] = conceptrecid.pid_value
    return conceptrecid


# By default both recid and conceptrecid will be RESERVED
RecordIdProviderV2.default_status_with_obj = PIDStatus.RESERVED


def versioned_recid_minter_v2(record_uuid, data):
    """Rserve the Concept RECID and create the RECID."""
    if 'conceptrecid' not in data:
        conceptrecid_minter_v2(data=data)
    else:
        # FIXME: Assuming its a version() call + Not nice here (use PIDRelations)
        data.pop('recid')

    recid = recid_minter_v2(record_uuid, data)

    return recid
