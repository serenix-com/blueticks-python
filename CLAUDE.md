# blueticks-python regeneration conventions

This file is the authoritative spec for a subagent regenerating the Python SDK
from `openapi.json`. The subagent sees this file, the OpenAPI spec, and the
current contents of the regenerated paths — nothing else. Everything it
produces must follow these rules.

## 1. Boundaries

### You MAY write:

- `src/blueticks/resources/*.py`
- `src/blueticks/resources/__init__.py`
- `src/blueticks/types/*.py`
- `src/blueticks/types/__init__.py`
- `tests/test_<resource>.py` — one per resource file

### You MUST NOT touch:

- `src/blueticks/_client.py`
- `src/blueticks/_transport.py`
- `src/blueticks/_errors.py`
- `src/blueticks/_base_resource.py`
- `src/blueticks/_version.py`
- `src/blueticks/__init__.py`
- `tests/conftest.py`
- `tests/test_client.py`
- `tests/test_transport.py`
- `tests/test_errors.py`
- `pyproject.toml`
- `CHANGELOG.md`
- `README.md`
- `LICENSE`
- `.github/workflows/**`
- `CLAUDE.md` (this file)

## 2. Types (OpenAPI schema → Pydantic model)

One file per response schema under `src/blueticks/types/<snake_name>.py`. Each
file defines one `pydantic.BaseModel` subclass.

- Class name: PascalCase of the schema's `title` or the operation's response
  name (e.g., `AccountResponse` → `Account`).
- Field names: snake_case, matching the spec (the spec is already snake_case).
- `model_config = ConfigDict(extra="ignore")` so new backend fields don't break
  old SDKs.

### Type mapping

| OpenAPI                             | Python                      |
| ----------------------------------- | --------------------------- |
| `string`                            | `str`                       |
| `string, format: date-time`         | `datetime.datetime`         |
| `integer`                           | `int`                       |
| `number`                            | `float`                     |
| `boolean`                           | `bool`                      |
| `array, items: <T>`                 | `list[<T>]`                 |
| `object` (inline)                   | nested `BaseModel`          |
| `nullable: true`                    | `Optional[T]`               |
| `enum: [a, b, c]`                   | `Literal["a", "b", "c"]`    |

Every file imports `from __future__ import annotations`.

### `types/__init__.py`

Re-export every public model alphabetically:

```python
from blueticks.types.account import Account
from blueticks.types.ping import Ping

__all__ = ["Account", "Ping"]
```

## 3. Resources (OpenAPI operation → Python method)

One file per path group under `src/blueticks/resources/<snake_name>.py`. Group
by the first path segment after `/v1/` — `/v1/account`, `/v1/account/usage`
all go in `resources/account.py`.

Each file defines one class:

```python
from blueticks._base_resource import BaseResource

class AccountResource(BaseResource):
    ...
```

### Method-name mapping (from the Feathers operation method)

| Feathers | Python           | When                                    |
| -------- | ---------------- | --------------------------------------- |
| `find`   | `list`           | response is paginated (top-level `data` array + `pagination`) |
| `find`   | `retrieve`       | response is a single object             |
| `get`    | `retrieve`       | always                                  |
| `create` | `create`         | always                                  |
| `patch`  | `update`         | always                                  |
| `remove` | `delete`         | always                                  |

### Method signatures

- Positional: path parameters only.
- Keyword-only (after `*,`): query parameters and body fields.
- Return type: the corresponding `types/*.py` model.
- Body: every method routes through `self._client._request(...)`. Never call
  `httpx` directly.
- Docstring: operation `summary` + `\n\n` + operation `description`, verbatim.

### Example

```python
from __future__ import annotations

from blueticks._base_resource import BaseResource
from blueticks.types.account import Account


class AccountResource(BaseResource):
    def retrieve(self) -> Account:
        """Fetch the authenticated account.

        Returns the account associated with the API key used for this request.
        """
        data = self._client._request("GET", "/v1/account")
        return Account.model_validate(data)
```

### `resources/__init__.py`

Re-export every resource class alphabetically:

```python
from blueticks.resources.account import AccountResource
from blueticks.resources.ping import PingResource

__all__ = ["AccountResource", "PingResource"]
```

## 4. Tests

One file per resource, named `tests/test_<resource>.py`.

### Per method: two tests

**Happy path.** Mock the transport to return the OpenAPI operation's `example`
response. Assert the method returns the typed model with the expected field
values.

**Error path.** Mock the transport to return a 401 with the standard envelope.
Assert `AuthenticationError` is raised with the expected `code`, `message`,
`request_id`.

Use the `mock_client` fixture from `tests/conftest.py`:

```python
def test_account_retrieve_returns_typed_model(mock_client) -> None:
    def handler(request):
        assert request.method == "GET"
        assert request.url.path == "/v1/account"
        return httpx.Response(200, content=json.dumps({
            "id": "acc_1",
            "name": "Acme",
            "timezone": "America/New_York",
            "created_at": "2026-04-22T10:00:00Z",
        }).encode())

    with mock_client(handler) as client:
        result = client.account.retrieve()
    assert isinstance(result, Account)
    assert result.id == "acc_1"
```

### Missing-required-field test

For every resource file, include one test where the server returns `{}` and
assert `pydantic.ValidationError` is raised.

## 5. After regeneration

The controller (`regenerate.sh` via `tools/regenerate-python.sh`) will run:

```bash
ruff format --check src tests
ruff check src tests
mypy src/blueticks
pytest -q
```

All four must pass. If any fail, the regeneration is rejected; fix the
underlying `CLAUDE.md` bug rather than the generated output.
