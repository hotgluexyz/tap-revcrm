"""HTTP API client (REST or GraphQL), including RevCRMStream base class."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import requests
from hotglue_singer_sdk.streams import RESTStream
from typing_extensions import override


class RevCRMStream(RESTStream):
    """RevCRM stream class."""

    records_jsonpath = "$.items[*]"

    @override
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via the ``api_url`` tap setting."""
        return self.config["api_url"].rstrip("/")

    @override
    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "ROI-CLIENT-CODE": self.config["client_code"],
        }

    @property
    def _access_token(self) -> str:
        """Obtain a RevCRM Auth0 access token for this tap process."""
        if not hasattr(self, "__access_token"):
            response = requests.post(
                self.config["token_url"],
                json={
                    "client_id": self.config["client_id"],
                    "client_secret": self.config["client_secret"],
                    "audience": "https://app.roicrm.net/api/1.0/",
                    "grant_type": "client_credentials",
                    "roi_client_code": self.config["client_code"],
                },
                timeout=30,
            )
            response.raise_for_status()
            self.__access_token = response.json()["access_token"]
        return self.__access_token

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Any | None:
        """Return token identifying next page or None if all records have been read.

        Args:
            response: A raw `requests.Response`_ object.
            previous_token: Previous pagination reference.

        Returns:
            Reference value to retrieve next page.

        .. _requests.Response:
            https://requests.readthedocs.io/en/latest/api/#requests.Response
        """
        page = response.json()
        if page["page"] >= page["total_pages"]:
            return None
        return page["page"] + 1

    @override
    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        return {
            **self.config["search_parameters"],
            "page": next_page_token or 1,
            "limit": self.config["per_page"],
            "include": "emails",
        }

    @override
    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        """As needed, append or transform raw data to match expected structure.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The updated record dictionary, or ``None`` to skip the record.
        """
        return row

    @override
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Emit resources from RevCRM's paginated ``items`` array."""
        yield from response.json()["items"]
