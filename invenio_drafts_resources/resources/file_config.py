# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Draft File config."""


from flask_resources.resources import ResourceConfig

from ..services import FileMetadataService, FileService


class DraftFileResourceConfig(ResourceConfig):
    """Draft file resource config."""

    list_route = "/records/<pid_value>/draft/files"
    item_route = "/records/<pid_value>/draft/files/<key>"


class DraftFileActionResourceConfig(ResourceConfig):
    """Draft file action resource config."""

    # QUESTIONs:
    # 1- Should the item_route be used for SingletonResource actually? Change
    #    in Flask-Resource would be needed
    # 2- Should the list_route instead precede download with "actions" to be in
    #    keeping with other actions endpoints?
    list_route = "/records/<pid_value>/draft/files/<key>/<action>"
