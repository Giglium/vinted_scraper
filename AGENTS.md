# AGENTS.md

## Project Overview

**vinted_scraper** is a Python package for scraping the Vinted marketplace. It supports both synchronous and asynchronous operations with automatic cookie management and typed responses.

- **Language**: Python (supports 3.8 – 3.14)
- **Development Python version**: 3.14 (see `.python-version`)
- **Package manager**: [uv](https://github.com/astral-sh/uv)
- **Build tool**: `uv_build`
- **HTTP client**: `httpx[brotli]`
- **License**: MIT

## Development Commands (Makefile)

All common tasks are available via the Makefile. Run `make help` for a quick reference.

| Command         | Description                                                           |
| --------------- | --------------------------------------------------------------------- |
| `make test`     | Run all unit tests (`uv run python -m unittest discover`)             |
| `make coverage` | Run tests with coverage report (source, XML, terminal)                |
| `make fmt`      | Format code: `no_implicit_optional`, `black`, `isort --profile black` |
| `make lint`     | Run Super Linter via Docker (comprehensive static analysis)           |
| `make build`    | Compile the library (`uv build`)                                      |
| `make docs`     | Generate API documentation with `pdoc`                                |
| `make clean`    | Remove build artifacts, coverage files, docs                          |
| `make all`      | Run `fmt`, `lint`, and `coverage` in sequence                         |

### Setup

```bash
uv sync   # Install all dependencies including dev group
```

### Testing

```bash
make test       # Run all unit tests
make coverage   # Run tests + generate coverage (source, XML, terminal report)
```

- Framework: **unittest** (standard library), not pytest
- Test discovery: `python -m unittest discover` from project root
- Tests live in `tests/` and import source as `from src.vinted_scraper import ...`
- Mocking: `unittest.mock` (`patch`, `MagicMock`, `AsyncMock`)
- Async tests use `unittest.IsolatedAsyncioTestCase`
- Sample data fixtures in `tests/samples/` (JSON and HTML files)
- Shared test utilities in `tests/utils/` (`_mock.py`, `_fs.py`)
- Coverage tool: `coverage` (generates `coverage.xml` and terminal report via `make coverage`); the suite currently keeps source at 100%

### Formatting

```bash
make fmt
```

Runs in order:

1. `no_implicit_optional` — rewrites implicit `Optional` types
2. `black` — code formatter
3. `isort --profile black` — import sorter (black-compatible)

### Linting

```bash
make lint
```

Runs [Super Linter](https://github.com/super-linter/super-linter) v8.6.0 inside Docker. Disabled validators: `PYTHON_MYPY`, `TRIVY`, `BIOME_FORMAT`, `BIOME_LINT`, `PYTHON_RUFF`, `PYTHON_RUFF_FORMAT`. The linter also auto-fixes YAML, Markdown, JSON, Python (black/isort), and GitHub Actions files.

## Architecture

### Layer Diagram

```bash
┌──────────────────────────────────────────────────┐
│            Public API (__init__.py)              │
│  VintedScraper / AsyncVintedScraper (typed)      │
│  VintedWrapper  / AsyncVintedWrapper (raw JSON)  │
└──────────────────────────────────────────────────┘
        │                        │
        ▼                        ▼
┌──────────────────┐  ┌──────────────────────────┐
│  _scraper.py     │  │  _async_scraper.py       │
│  (typed models)  │  │  (typed models, async)   │
└──────────────────┘  └──────────────────────────┘
        │                        │
        ▼                        ▼
┌──────────────────┐  ┌──────────────────────────┐
│  _wrapper.py     │  │  _async_wrapper.py       │
│  (httpx.Client)  │  │  (httpx.AsyncClient)     │
└──────────────────┘  └──────────────────────────┘
        │                        │
        └──────────┬─────────────┘
                   ▼
        ┌──────────────────────┐
        │  _base_wrapper.py    │
        │  (shared non-I/O     │
        │   logic: validation, │
        │   headers, retry,    │
        │   cookie handling)   │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │    utils/            │
        │  _constants.py       │
        │  _headers.py         │
        │  _html.py            │
        │  _httpx.py           │
        │  _log.py             │
        │  _user_agent.py      │
        │  agents.json         │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │    models/           │
        │  VintedJsonModel     │
        │  VintedItem          │
        │  VintedUser          │
        │  VintedBrand         │
        │  VintedImage         │
        │  VintedMedia         │
        │  VintedHighResolution│
        │  VintedSession       │
        └──────────────────────┘
```

### Key Architectural Choices

1. **Wrapper vs Scraper split**
   - `VintedWrapper` / `AsyncVintedWrapper` return **raw JSON dictionaries**
   - `VintedScraper` / `AsyncVintedScraper` inherit from the wrappers and return **typed dataclass models** (`VintedItem`, `VintedJsonModel`)
   - This lets consumers choose their preferred abstraction level

2. **Shared base class (`BaseVintedWrapper`)**
   - All non-I/O logic (URL validation, header building, cookie response processing, retry/sleep calculation, response parsing) lives in the base class
   - Sync and async variants only implement the I/O-specific parts (`httpx.Client` vs `httpx.AsyncClient`)
   - Avoids code duplication between sync and async paths

3. **Dataclass-based design**
   - All wrappers, scrapers, and models use `@dataclass`
   - Models auto-populate attributes from raw JSON via `__post_init__` and `__dict__.update`
   - Subscript access (`item["key"]`) is also supported on models
   - **Intentional design:** `VintedJsonModel.__post_init__` uses `self.__dict__.update(self.json_data)` without filtering keys. This is deliberate. It allows consumers to access any API field as an attribute even if the library hasn't declared it yet. The trade-off (dunder keys or field name collisions) is accepted because Vinted's API does not return such keys in practice.

4. **Async factory pattern**
   - `AsyncVintedWrapper` cannot fetch cookies in `__post_init__` (not async), so a `create()` classmethod factory is provided
   - Alternatively, users can pass a prefetched `session=VintedSession(...)`

5. **Session management and retry logic**
   - The identity (cookies + anonymous ID, plus an optional CSRF token, plus the market `locale`) is a single `VintedSession` object (`models/_session.py`), passed to the constructor as `session=` and stored on the wrapper as `self.session`
   - `fetch_session()` reads the identity from one landing-page request and returns a `VintedSession`
   - `refresh_session()` calls it, replaces `self.session` with the fetched one, and returns it (a refresh fully replaces the identity rather than merging)
   - A fetch happens only when `_needs_session()` is true, i.e. no session was passed or `VintedSession.is_empty()`; passing any identity part skips it
   - A landing-page fetch only accepts a `200` response whose resulting session `is_usable()` (has both cookies and an anonymous ID). A `200` that hands over an unusable identity is treated as a failure: it falls through to the backoff/retry loop rather than being returned, so an anti-bot page that returns `200` without them does not silently produce a broken wrapper
   - **CSRF token is not auto-fetched.** The API currently accepts calls without it, so `build_session()` skips parsing it out of the page HTML. It stays a supported `VintedSession` field (sent when set, and a caller may supply one), and the extraction machinery (`utils/_html.py::extract_csrf_token`, `CSRF_MARKER`) is kept so it can be re-enabled by a one-line change in `build_session()`
   - `build_session()` (in `utils/_session.py`) is the single place that assembles a `VintedSession` from a landing-page response and logs a `warning` for each **fetched** part the page did not hand over (cookies, anon ID, and the `locale` read from `<html lang>`). The `VintedSession` model itself is silent on construction, so a caller-supplied partial session (allowed to be incomplete) does not warn
   - **Market locale.** Vinted serves one host per market and stamps that market's `language-REGION` tag on the landing page's `<html lang>` (e.g. `nl-NL`, `cs-CZ`); that tag is exactly the value the APIs `Locale` header expects.
     `build_session()` reads it (`utils/_html.py::extract_locale_from_html`) into `VintedSession.locale`, so it round-trips when a caller reuses `session=previous.session`.
     The `Locale` sent on each request is resolved by `BaseVintedWrapper._locale()`, most specific first: the constructor `locale=` override → the current session's `locale` → a best-effort guess from the base URL (`utils/_headers.py::locale_from_base_url`, full tags, defaulting to `en-US`). Resolved per call, so a session refresh is reflected immediately.
     `locale` is metadata, not a credential: it is deliberately ignored by `is_empty()`/`is_usable()` (a session carrying only a locale still triggers a real fetch), and a page with no `<html lang>` still yields a usable session — it just warns and falls back to the URL guess
   - **Intentional design:** `VintedSession` keeps its `cookies`, `csrf_token` and `anon_id` in its `repr` even though they are secrets. This is deliberate: the library exists to expose the identity so callers can inspect, persist and reuse it (`session=previous.session`). Hiding the values would work against that. Callers are responsible for not leaking a session `repr` into untrusted logs
   - Automatic on construction (sync) or via `create()` (async)
   - On HTTP 401, the wrapper transparently refreshes the session and retries
   - Exponential backoff on failures (`RETRY_BASE_SLEEP ** attempt`)

6. **Streamed page reads (OpenGraph, locale + CSRF)**
   - The JSON item endpoint (`/api/v2/items/{id}/details`) is blocked by anti-bot protection, so `item()` reads OpenGraph `<meta>` tags from the public item page `<head>`
   - `_stream_until(client, url, headers, stop_marker)` reads a page chunk by chunk and stops at `stop_marker`, so the full body is never downloaded: `item()` stops at `</head>`; the session fetch stops at the `CSRF_TOKEN` marker, which can sit after the `<head>`
   - The session fetch's streamed fragment has a live use: it parses the market `locale` from the `<html lang>` tag (see section 5), which sits at the very start of the document. Cookies and the anon ID come from the response object/headers, not the body. The read keeps going to the `CSRF_TOKEN` marker even though the token is not currently parsed, so re-enabling CSRF extraction stays a one-line change
   - The chunk-boundary bookkeeping (marker spanning two chunks, case-insensitive, chunks shorter than the marker) lives once in `utils/_html.py::ChunkAccumulator`, reused by both wrappers

7. **Two hosts, two httpx clients**
   - Catalog search moved off `/api/v2/catalog/items` to `/svc-catalogue/items`, served from the `api.` host (e.g. `https://api.vinted.com`); the landing page and item page use the site `www.` host
   - Each wrapper holds two clients: `_client` (site host) and `_api_client` (`api.` host). Both are built-in `__post_init__` from the configs returned by `_validate_and_init()`, and both are closed by the context manager and `__del__`
   - Endpoints stay **relative**: `curl(endpoint, params, *, api_endpoint=False)` concatenates the endpoint against the chosen client's `base_url` — the `api.` client when `api_endpoint=True`, the site client otherwise. The `api_endpoint` flag is part of the public `curl` API, so callers can target either host; `search()` uses it internally. `_search_endpoint()` returns the relative `/svc-catalogue/items`
   - `baseurl` may be passed with or without `www.`; `_validate_and_init()` normalizes it to the `www.` site form via `site_base_url()` and derives the `api.` host via `api_base_url()` (both handle `www.`/bare input)
   - The API needs an anonymous ID (returned as the `X-Anon-Id` response header), stored on the wrapper and refreshed together with the cookie. A CSRF token is sent as `X-Csrf-Token` when the session has one, but it is not auto-fetched and the API currently accepts calls without it (see section 5)
   - The `Locale` header selects the market (currency, listings) and is **not** hardcoded: it is resolved per request by `_locale()` (see section 5). `get_curl_headers`/`get_cookie_headers` take the resolved `locale` as a **required** argument and derive `Accept-Language` from it; deriving the fallback from a base URL is the caller's job (`locale_from_base_url`), not the builders'
   - `search()` and `curl()` deliberately share one header set (`get_curl_headers`) so every API call is sent with identical headers

8. **Private module convention**
   - All implementation modules are prefixed with `_` (e.g., `_wrapper.py`, `_base_wrapper.py`)
   - Public API is explicitly exported via `__init__.py` and `__all__`

9. **Error handling in models**
   - Price parsing (`_parse_price` and inline `VintedItem.__post_init__`) uses `try/except` to gracefully handle malformed values (e.g., non-numeric strings, missing dict keys). Invalid prices result in `None` rather than raising exceptions.
   - Models should never raise on construction due to unexpected API data; fields default to `None` when parsing fails.

## Source Layout

```bash
src/vinted_scraper/
├── __init__.py              # Public API exports
├── _base_wrapper.py         # Shared base class (non-I/O logic)
├── _wrapper.py              # Sync wrapper (site + api httpx.Client)
├── _async_wrapper.py        # Async wrapper (site + api httpx.AsyncClient)
├── _scraper.py              # Sync scraper (typed models)
├── _async_scraper.py        # Async scraper (typed models)
├── models/
│   ├── __init__.py          # Model exports
│   ├── _json_model.py       # Base model class
│   ├── _item.py             # VintedItem
│   ├── _user.py             # VintedUser
│   ├── _brand.py            # VintedBrand
│   ├── _image.py            # VintedImage
│   ├── _media.py            # VintedMedia
│   ├── _high_resolution.py  # VintedHighResolution
│   └── _session.py           # VintedSession (cookies + anon id + market locale; optional CSRF token)
├── utils/
│   ├── __init__.py          # Utility exports
│   ├── _constants.py        # API paths, hosts, timeouts, status codes
│   ├── _headers.py          # URL validation, host routing, HTTP headers
│   ├── _html.py             # HTML head parsing (OpenGraph tags, <html lang> locale, CSRF token)
│   ├── _httpx.py            # httpx config, cookie and anon-id extraction
│   ├── _log.py              # Structured logging helpers
│   ├── _user_agent.py       # User agent loading and selection
│   └── agents.json          # User agent list (auto-updated)
└── py.typed                 # PEP 561 marker

tests/
├── samples/                 # JSON/HTML fixtures
├── utils/
│   ├── _mock.py             # Mock factories and setup helpers
│   └── _fs.py              # File reading utilities for fixtures
├── test_wrapper.py          # Sync wrapper + scraper tests
├── test_async_wrapper.py    # Async wrapper + scraper tests
├── test_wrapper_edge_cases.py
├── test_json_model.py
├── test_models.py
├── test_utils_httpx.py
├── test_utils_log.py
└── test_utils_misc.py

examples/
├── scraper.py               # Sync scraper usage
├── wrapper.py               # Sync wrapper usage
├── async_scraper.py         # Async scraper usage
└── async_wrapper.py         # Async wrapper usage
```

## CI/CD

- **Tests**: Run on every push/PR across Python 3.8–3.14 matrix (`uv run --locked python -m unittest discover`)
- **Linting**: Super Linter on push to main and PRs
- **Coverage**: Separate workflow generates coverage reports
- **Docs**: Auto-generated with `pdoc`
- **Release**: Build and publish via `uv build`
- **User agents**: Periodically auto-updated via workflow

## Conventions

- Docstrings: Google style (Args/Returns/Raises sections)
- Type hints: Full annotations, `typing.Final` for constants
- Naming: private modules prefixed with `_`, public exports in `__all__`
- Error handling: `RuntimeError` for unrecoverable API/network errors
- Logging: Structured via dedicated `_log.py` helpers, one logger per module
- Imports: absolute from `src.vinted_scraper` in tests, relative within the package
- URL validation: `baseurl` must match `^https://(www\.)?[\w.-]+\.\w{2,}$` (HTTPS enforced, `www.` optional, no path/port/query allowed). It is then normalized to its `www.` site form, and the `api.` host is derived from it
