# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""User records resource."""

from flask_resources.resources import ResourceConfig


class UserRecordsResourceConfig(ResourceConfig):
    """Deposit resource config."""

    list_route = "/user/records"
