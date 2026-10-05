"""Stream type classes for tap-revcrm."""

from __future__ import annotations

from typing import ClassVar

from hotglue_singer_sdk import typing as th  # JSON Schema typing helpers
from typing_extensions import override

from tap_revcrm.client import RevCRMStream


class DonorsStream(RevCRMStream):
    """Stream for RevCRM donors with their included email addresses."""

    name = "donors"
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

    @override
    def post_process(self, row: dict, context: dict | None = None) -> dict:
        """Add per-email opt-in status while keeping donors as the sole stream."""
        do_not_contact = str(row.get("do_not_contact", "false")).lower() == "true"
        for email in row.get("email_addresses", []):
            email["opt_in"] = email.get("contact_status") == "Y" and not do_not_contact
        return row
