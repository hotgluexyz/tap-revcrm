"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import json

import pytest
from hotglue_singer_sdk.testing import get_standard_tap_tests
from requests import Response

from tap_revcrm.streams import ContactsStream
from tap_revcrm.tap import TapRevCRM

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "client_id": "placeholder",
    "client_secret": "placeholder",
    "client_code": "placeholder",
    "search_parameters": {"email": "person@example.org"},
}

# _test_stream_connections makes live HTTP calls; excluded by default.
# Replace SAMPLE_CONFIG placeholders with real credentials and call it directly.
_STANDARD_TESTS = [
    t
    for t in get_standard_tap_tests(TapRevCRM, config=SAMPLE_CONFIG)
    if getattr(t, "__name__", "") != "_test_stream_connections"
]


@pytest.mark.parametrize("test_func", _STANDARD_TESTS)
def test_standard(test_func):
    """Run built-in SDK tap tests (CLI output and catalog discovery)."""
    test_func()


def test_contacts_flatten_email_and_derives_opt_in():
    response = Response()
    response.status_code = 200
    response._content = json.dumps(
        {
            "items": [
                {
                    "roi_family_id": "42",
                    "name_first": "Ada",
                    "name_last": "Lovelace",
                    "do_not_contact": "false",
                    "email_addresses": [
                        {
                            "email_id": "99",
                            "email_address": "ada@example.org",
                            "contact_status": "Y",
                        }
                    ],
                },
                {
                    "roi_family_id": "43",
                    "do_not_contact": "true",
                    "email_addresses": [
                        {
                            "email_id": "100",
                            "email_address": "opted-out@example.org",
                            "contact_status": "Y",
                        }
                    ],
                },
            ]
        }
    ).encode()

    records = list(ContactsStream.parse_response(object.__new__(ContactsStream), response))

    assert records[0]["opt_in"] is True
    assert records[0]["name_first"] == "Ada"
    assert records[1]["opt_in"] is False
