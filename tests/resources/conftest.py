# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from flask_principal import Identity, Need, UserNeed
from mock_module.resource import DraftActionResource, \
    DraftActionResourceConfig, DraftResource, DraftResourceConfig, \
    DraftVersionResource, DraftVersionResourceConfig, RecordResource, \
    RecordResourceConfig
from mock_module.service import Service, ServiceConfig


@pytest.fixture(scope="module")
def record_resource():
    """Resource."""
    # FIXME
    # This should work but doesn't because the application context is checked
    # to see if it's been overridden in the config.
    # return Resource(service=Service())
    return RecordResource(
        config=RecordResourceConfig,
        service=Service(config=ServiceConfig)
    )


@pytest.fixture(scope="module")
def draft_resource():
    """Resource."""
    # FIXME
    # This should work but doesn't because the application context is checked
    # to see if it's been overridden in the config.
    # return Resource(service=Service())
    return DraftResource(
        config=DraftResourceConfig,
        service=Service(config=ServiceConfig)
    )


@pytest.fixture(scope="module")
def action_resource():
    """Action Resource."""
    # FIXME
    # This should work but doesn't because the application context is checked
    # to see if it's been overridden in the config.
    # return Resource(service=Service())
    return DraftActionResource(
        config=DraftActionResourceConfig,
        service=Service(config=ServiceConfig)
    )


@pytest.fixture(scope="module")
def version_resource():
    """Version Resource."""
    # FIXME
    # This should work but doesn't because the application context is checked
    # to see if it's been overridden in the config.
    # return Resource(service=Service())
    return DraftVersionResource(
        config=DraftVersionResourceConfig,
        service=Service(config=ServiceConfig)
    )


@pytest.fixture(scope="module")
def base_app(base_app, record_resource, draft_resource, action_resource,
             version_resource):
    """Application factory fixture."""
    base_app.register_blueprint(record_resource.as_blueprint('mock_record'))
    base_app.register_blueprint(draft_resource.as_blueprint('mock_draft'))
    base_app.register_blueprint(action_resource.as_blueprint('mock_action'))
    base_app.register_blueprint(version_resource.as_blueprint('mock_version'))
    # FIXME: Why is this commented out? Also in records-resources
    # base_app.register_error_handler(HTTPException, handle_http_exception)
    yield base_app


@pytest.fixture(scope="module")
def identity_simple():
    """Simple identity fixture."""
    i = Identity(1)
    i.provides.add(UserNeed(1))
    i.provides.add(Need(method='system_role', value='any_user'))
    return i
