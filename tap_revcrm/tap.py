"""RevCRM tap class."""

from __future__ import annotations

from hotglue_singer_sdk import Stream, Tap
from hotglue_singer_sdk import typing as th  # JSON schema typing helpers
from typing_extensions import override

from tap_revcrm.streams import (
    ConstituentsStream,
    ContactsStream,
)

STREAM_TYPES = [
    ConstituentsStream,
    ContactsStream,
]


class TapRevCRM(Tap):
    """Singer tap for RevCRM."""

    name = "tap-revcrm"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Retained for Singer state compatibility; RevCRM donor search has no date filter.",
            default="2000-01-01T00:00:00Z",
        ),
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            description="Auth0 machine-to-machine application client ID.",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            description="Auth0 machine-to-machine application client secret.",
        ),
        th.Property(
            "client_code",
            th.StringType,
            required=True,
            description="RevCRM client database code sent as roi_client_code and ROI-CLIENT-CODE.",
        ),
        th.Property(
            "api_url",
            th.StringType,
            description="RevCRM API base URL.",
            default="https://app.roicrm.net/api/1.0",
        ),
        th.Property(
            "token_url",
            th.StringType,
            description="Auth0 client-credentials token endpoint.",
            default="https://roisolutions.us.auth0.com/oauth/token",
        ),
        th.Property(
            "per_page",
            th.IntegerType,
            description="Number of donors requested per RevCRM API page.",
            default=100,
        ),
        th.Property(
            "search_parameters",
            th.ObjectType(),
            required=True,
            description=(
                "At least one valid RevCRM donor search field, such as "
                "{'account-flag': 'MEMBER'} or {'email': 'person@example.org'}."
            ),
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapRevCRM.cli()
