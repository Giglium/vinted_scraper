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
- Coverage tool: `coverage` (generates `coverage.xml` and terminal report via `make coverage`)

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
        │  _httpx.py           │
        │  _misc.py            │
        │  _log.py             │
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
   - Alternatively, users can pass a prefetched `session_cookie`

5. **Cookie management and retry logic**
   - Automatic session cookie fetch on construction (sync) or via `create()` (async)
   - On HTTP 401, the wrapper transparently refreshes the cookie and retries
   - Exponential backoff on cookie fetch failures (`RETRY_BASE_SLEEP ** attempt`)

6. **Item metadata via OpenGraph scraping**
   - The JSON item endpoint (`/api/v2/items/{id}/details`) is blocked by anti-bot protection
   - Item data is extracted from OpenGraph `<meta>` tags in the public HTML item page `<head>`
   - Only the `<head>` section is streamed (efficient, avoids downloading full page)

7. **Private module convention**
   - All implementation modules are prefixed with `_` (e.g., `_wrapper.py`, `_base_wrapper.py`)
   - Public API is explicitly exported via `__init__.py` and `__all__`

8. **Error handling in models**
   - Price parsing (`_parse_price` and inline `VintedItem.__post_init__`) uses `try/except` to gracefully handle malformed values (e.g., non-numeric strings, missing dict keys). Invalid prices result in `None` rather than raising exceptions.
   - Models should never raise on construction due to unexpected API data; fields default to `None` when parsing fails.

## Source Layout

```bash
src/vinted_scraper/
├── __init__.py              # Public API exports
├── _base_wrapper.py         # Shared base class (non-I/O logic)
├── _wrapper.py              # Sync wrapper (httpx.Client)
├── _async_wrapper.py        # Async wrapper (httpx.AsyncClient)
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
│   └── _high_resolution.py  # VintedHighResolution
├── utils/
│   ├── __init__.py          # Utility exports
│   ├── _constants.py        # API paths, timeouts, status codes
│   ├── _httpx.py            # httpx config and cookie extraction
│   ├── _misc.py             # User agents, URL validation, headers, HTML parsing
│   ├── _log.py              # Structured logging helpers
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
- URL validation: `baseurl` must match `^https://(www\.)?[\w.-]+\.\w{2,}$` (HTTPS enforced, `www.` optional, no path/port/query allowed)
