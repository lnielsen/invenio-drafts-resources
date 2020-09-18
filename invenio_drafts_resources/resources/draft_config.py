# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from flask_resources.resources import ResourceConfig, Response
from flask_resources.serializers import JSONSerializer


class DraftResourceConfig(ResourceConfig):
    """Draft resource config."""

    list_route = "/records/<pid_value>/draft"


class DraftActionResourceConfig(ResourceConfig):
    """Draft action resource config."""

    list_route = "/records/<pid_value>/draft/actions/<action>"
    action_commands = {
        "publish": "publish",
    }


class DraftVersionResourceConfig(ResourceConfig):
    """Draft resource config."""

    list_route = "/records/<pid_value>/versions"
