# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Deposits Resources."""

from flask_resources import CollectionResource

from .userrecords_config import UserRecordsResourceConfig


class UserRecordsResource(CollectionResource):
    """User records resource."""

    default_config = UserRecordsResourceConfig

    def search(self, *args, **kwargs):
        """Perform a search over the items.

        GET /user/records
        """
        return STUB_LIST_RESULT
