"""Example resource."""

from invenio_records_resources.resources import \
    RecordResource as RecordResourceBase
from invenio_records_resources.resources import \
    RecordResourceConfig as RecordResourceConfigBase

from invenio_drafts_resources.resources import \
    DraftActionResource as DraftActionResourceBase
from invenio_drafts_resources.resources import \
    DraftActionResourceConfig as DraftActionResourceConfigBase
from invenio_drafts_resources.resources import \
    DraftResource as DraftResourceBase
from invenio_drafts_resources.resources import \
    DraftResourceConfig as DraftResourceConfigBase
from invenio_drafts_resources.resources import \
    DraftVersionResource as DraftVersionResourceBase
from invenio_drafts_resources.resources import \
    DraftVersionResourceConfig as DraftVersionResourceConfigBase


class RecordResourceConfig(RecordResourceConfigBase):
    """Mock service configuration."""

    list_route = "/mocks"
    item_route = f"{list_route}/<pid_value>"


class RecordResource(RecordResourceBase):
    """Mock service."""

    default_config = RecordResourceConfig


class DraftResourceConfig(DraftResourceConfigBase):
    """Mock service configuration."""

    list_route = "/mocks/<pid_value>/draft"


class DraftResource(DraftResourceBase):
    """Mock service."""

    default_config = DraftResourceConfig


class DraftActionResourceConfig(DraftActionResourceConfigBase):
    """Mock service configuration."""

    list_route = "/mocks/<pid_value>/draft/actions/<action>"

    action_commands = {
        "publish": "publish",
        "command": "not_implemented"
    }


class DraftActionResource(DraftActionResourceBase):
    """Mock service."""

    default_config = DraftActionResourceConfig


class DraftVersionResourceConfig(DraftVersionResourceConfigBase):
    """Mock service configuration."""

    list_route = "/mocks/<pid_value>/versions"


class DraftVersionResource(DraftVersionResourceBase):
    """Mock service."""

    default_config = DraftVersionResourceConfig
