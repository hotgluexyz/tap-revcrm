"""Stream type classes for tap-revcrm."""

from __future__ import annotations

from collections.abc import Iterable
from typing import ClassVar

import requests
from hotglue_singer_sdk import typing as th  # JSON Schema typing helpers
from typing_extensions import override

from tap_revcrm.client import RevCRMStream


class ConstituentsStream(RevCRMStream):
    """Stream for ``constituents``."""

    name = "constituents"
    path = "/donors/"
    primary_keys: ClassVar[list[str]] = ["roi_family_id"]
    replication_key = "modified_date"
    schema = th.PropertiesList(
        th.Property("roi_family_id", th.StringType),
        th.Property("roi_id", th.StringType),
        th.Property("name_first", th.StringType),
        th.Property("name_last", th.StringType),
        th.Property("name_full", th.StringType),
        th.Property("do_not_contact", th.StringType),
        th.Property("is_deceased", th.StringType),
        th.Property("account_status", th.StringType),
        th.Property("modified_date", th.DateTimeType),
        th.Property("email_addresses", th.ArrayType(th.ObjectType())),
    ).to_dict()


class ContactsStream(RevCRMStream):
    """Stream for ``contacts``."""

    name = "contacts"
    path = "/donors/"
    primary_keys: ClassVar[list[str]] = ["email_id"]
    replication_key = "last_change_date"
    schema = th.PropertiesList(
        th.Property("email_id", th.StringType),
        th.Property("email_address", th.StringType),
        th.Property("email_type", th.StringType),
        th.Property("contact_status", th.StringType),
        th.Property("opt_in", th.BooleanType),
        th.Property("roi_family_id", th.StringType),
        th.Property("roi_id", th.StringType),
        th.Property("name_first", th.StringType),
        th.Property("name_last", th.StringType),
        th.Property("modified_date", th.DateTimeType),
        th.Property("last_change_date", th.DateTimeType),
    ).to_dict()

    @override
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Flatten included RevCRM email resources into contact records."""
        for donor in response.json()["items"]:
            for email in donor.get("email_addresses", []):
                yield {
                    **email,
                    "roi_family_id": donor["roi_family_id"],
                    "roi_id": donor.get("roi_id"),
                    "name_first": donor.get("name_first"),
                    "name_last": donor.get("name_last"),
                    "modified_date": donor.get("modified_date"),
                    "opt_in": (
                        email.get("contact_status") == "Y"
                        and str(donor.get("do_not_contact", "false")).lower() != "true"
                    ),
                }
