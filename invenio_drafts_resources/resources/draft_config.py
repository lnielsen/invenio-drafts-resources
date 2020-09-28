# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from flask_resources.errors import HTTPJSONException, create_errormap_handler
from invenio_records_resources.resources import RecordResourceConfig


class DraftResourceConfig(RecordResourceConfig):
    """Draft resource config."""

    list_route = "/records/<pid_value>/draft"
    item_route = None


class DraftActionResourceConfig(RecordResourceConfig):
    """Draft action resource config."""

    list_route = "/records/<pid_value>/draft/actions/<action>"
    item_route = None  # To avoid issues, due to inheritance.

    actions = {
        "publish": "publish",
    }


class DraftVersionResourceConfig(RecordResourceConfig):
    """Draft resource config."""

    list_route = "/records/<pid_value>/versions"
    # TODO: REVISIT
