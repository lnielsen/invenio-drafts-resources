# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from flask import abort, g
from flask_resources import CollectionResource, SingletonResource
from flask_resources.context import resource_requestctx
from invenio_records_resources.config import ConfigLoaderMixin

from ..services import RecordDraftService
from .draft_config import DraftActionResourceConfig, DraftResourceConfig, \
    DraftVersionResourceConfig
from .errors import ActionNotImplementedError


class DraftResource(SingletonResource, ConfigLoaderMixin):
    """Draft resource."""

    default_config = DraftResourceConfig

    def __init__(self, config=None, service=None):
        """Constructor."""
        super(DraftResource, self).__init__(config=self.load_config(config))
        self.service = service or RecordDraftService()

    def read(self):
        """Edit a draft.

        GET /records/:pid_value/draft
        """
        item = self.service.read_draft(
            resource_requestctx.route["pid_value"],
            g.identity,
            links_config=self.config.links_config,
        )
        return item.to_dict(), 200

    def create(self):
        """Edit a record.

        POST /records/:pid_value/draft
        """
        item = self.service.edit(
            resource_requestctx.route["pid_value"],
            g.identity,
            links_config=self.config.links_config,
        )
        return item.to_dict(), 201

    def update(self):
        """Update a draft.

        PUT /records/:pid_value/draft
        """
        data = resource_requestctx.request_content
        item = self.service.update_draft(
            resource_requestctx.route["pid_value"],
            g.identity,
            data,
            links_config=self.config.links_config,
            revision_id=resource_requestctx.headers.get("if_match"),
        )
        return item.to_dict(), 200

    def delete(self):
        """Delete a draft.

        DELETE /records/:pid_value/draft
        """
        self.service.delete_draft(
            resource_requestctx.route["pid_value"],
            g.identity,
            revision_id=resource_requestctx.headers.get("if_match"),
        )
        return None, 204


class DraftVersionResource(CollectionResource, ConfigLoaderMixin):
    """Draft version resource."""

    default_config = DraftVersionResourceConfig

    def __init__(self, service=None, config=None):
        """Constructor."""
        super(DraftVersionResource, self).__init__(
            config=self.load_config(config))
        self.service = service or RecordDraftService()

    def search(self):
        """Perform a search over the items.

        GET /records/:pid_value/versions
        """
        # TODO: IMPLEMENT ME!
        return self.service.search(), 200

    def create(self):
        """Create a new version.

        POST /records/:pid_value/versions
        """
        item = self.service.new_version(
            resource_requestctx.route["pid_value"],
            g.identity
        )
        return item.to_dict(), 201


class DraftActionResource(SingletonResource, ConfigLoaderMixin):
    """Draft action resource."""

    default_config = DraftActionResourceConfig

    def __init__(self, service=None, config=None):
        """Constructor."""
        super(DraftActionResource, self).__init__(
            config=self.load_config(config))
        self.service = service or RecordDraftService()

    def create(self):
        """Any POST business logic.

        POST /records/:pid_value/actions/:action
        """
        action = resource_requestctx.route["action"]
        try:
            cmd_name = self.config.action_commands[action]
            cmd_func = getattr(self.service, cmd_name)
        except KeyError:
            raise abort(404)
        except AttributeError:
            raise ActionNotImplementedError(cmd_name)

        # NOTE: Due to the route we assume the commands only need
        # id_ and identity
        item = cmd_func(
            resource_requestctx.route["pid_value"],
            g.identity
        )
        return item.to_dict(), 202
