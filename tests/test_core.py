"""Tests standard tap features using the built-in SDK tests library."""

import datetime

import pytest
from hotglue_singer_sdk.testing import get_standard_tap_tests

from tap_revcrm.streams import DonorsStream
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


def test_donors_add_per_email_opt_in_status():
    donor = {
        "do_not_contact": "false",
        "email_addresses": [{"contact_status": "Y"}],
    }
    opted_out_donor = {
        "do_not_contact": "true",
        "email_addresses": [{"contact_status": "Y"}],
    }

    assert DonorsStream.post_process(object.__new__(DonorsStream), donor)["email_addresses"][0][
        "opt_in"
    ]
    assert not DonorsStream.post_process(object.__new__(DonorsStream), opted_out_donor)[
        "email_addresses"
    ][0]["opt_in"]
