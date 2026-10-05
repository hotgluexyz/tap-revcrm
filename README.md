# tap-revcrm

A [Singer](https://www.singer.io/) tap that extracts data from **RevCRM**. It is built with [hotglue-singer-sdk](https://github.com/hotgluexyz/HotglueSingerSDK) and speaks the standard Singer message protocol on stdout, so you can pair it with any compatible target.

## Features

- OAuth 2.0 client-credentials authentication through RevCRM's Auth0 tenant.
- RevCRM `ROI-CLIENT-CODE` request header for tenant isolation.
- Paginated donor extraction with email sub-resources included in each page.
- A boolean `opt_in` contact field: true only when the email `contact_status` is `Y` and the donor is not marked `do_not_contact`.

### Streams

| Stream | Endpoint / notes | Primary key | Replication key |
| ------ | ---------------- | ----------- | ----------------- |
| `constituents` | `GET /donors/?include=emails` | `roi_family_id` | `modified_date` |
| `contacts` | Email resources flattened from `GET /donors/?include=emails` | `email_id` | `last_change_date` |

RevCRM allows at most 500 requests per rolling five-minute window. Its donor endpoint requires a search criterion and returns at most 999 matching donors; configure the criterion with `search_parameters`.

## Requirements

- Python **3.10+** (see `requires-python` in `pyproject.toml`).

## Installation

1. **Clone** this repository and `cd` into the project directory.
2. **Create `config.json`** in the project root with your credentials and settings (see [Configuration](#configuration) for the fields and an example).
3. **Create a virtual environment** and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, use `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

4. **Install the package** in editable mode:

```bash
pip install -e .
```

5. **Run the tap** (with the venv still activated):

```bash
tap-revcrm --help
```

## Configuration

| Setting | Type | Required | Default | Description |
| ------- | ---- | -------- | ------- | ----------- |
| `client_id` | string | yes | — | Auth0 machine-to-machine application client ID. |
| `client_secret` | string | yes | — | Auth0 machine-to-machine application client secret. |
| `client_code` | string | yes | — | RevCRM tenant/client database code. |
| `search_parameters` | object | yes | — | Valid donor search criterion required by RevCRM, e.g. `{"account-flag":"MEMBER"}`. |
| `api_url` | string | no | `https://app.roicrm.net/api/1.0` | Base URL for the production RevCRM API. |
| `token_url` | string | no | `https://roisolutions.us.auth0.com/oauth/token` | Auth0 client-credentials endpoint. |
| `per_page` | integer | no | `100` | Number of donors per request (maximum 100). |

Run `tap-revcrm --about` (or `tap-revcrm --about --format=markdown`) for the authoritative schema for your installed version.

### Example `config.json`

```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "client_code": "YOUR_CLIENT_CODE",
  "search_parameters": {"account-flag": "MEMBER"}
}
```

Do not commit real credentials. Prefer environment variables or a secrets manager in production.

### Environment-based config

You can load settings from the process environment using `--config=ENV` (the SDK merges env into config). Env names follow the tap’s setting keys (see `tap-revcrm --about`).

## Usage

With your virtual environment **activated** and `config.json` in place:

Discover stream catalog:

```bash
tap-revcrm --config config.json --discover > catalog.json
```

Run a sync (with optional state):

```bash
tap-revcrm --config config.json --catalog catalog.json --state state.json
```

Pipe to any Singer target:

```bash
tap-revcrm --config config.json --catalog catalog.json | target-jsonl
```

Inspect built-in settings and stream metadata:

```bash
tap-revcrm --about
```

## API documentation

See the [ROI RevCRM REST API](https://app.roicrm.net/api/help/). Its Auth0 token request requires `client_id`, `client_secret`, `roi_client_code`, the `client_credentials` grant, and the audience `https://app.roicrm.net/api/1.0/`.


## License
MIT — see `LICENSE` and `pyproject.toml`.
