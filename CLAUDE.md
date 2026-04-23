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

### You MAY write (only, with narrow constraints):

- `src/blueticks/_client.py` — **only** to keep the `Blueticks` class's resource attachments and method return types in sync with the resources/types you regenerate. Specifically:
  - Add or remove `self.<resource> = <ResourceClass>(self)` attachments for resources you created or deleted.
  - Update the return-type annotation on helper methods (like `ping()`) that delegate to resource classes.
  - Keep any required `TYPE_CHECKING` forward-reference imports in sync.
  - Do NOT modify the constructor signature, `_request()`, env-var logic, `close()`, `__enter__`/`__exit__`, or any other method body.

### You MUST NOT touch:

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
| `nullable: true`                    | `Optional[T] = None` (see Python 3.9 note below) |
| `enum: [a, b, c]`                   | `Literal["a", "b", "c"]`    |

Every file imports `from __future__ import annotations`.

**Python 3.9 nullable field pattern:** Always write nullable Pydantic fields as `Optional[T] = None  # noqa: UP045`. NEVER use PEP 604 `T | None` syntax for nullable fields. On Python 3.9, Pydantic v2 evaluates field annotations at runtime via `typing.get_type_hints()`, which cannot resolve PEP 604 unions on 3.9 even with `from __future__ import annotations`. The `# noqa: UP045` suppresses ruff's modernization suggestion. This applies ONLY to Pydantic field annotations in `types/*.py`; other type hints (method signatures, variable annotations) can use modern `X | Y` syntax freely.

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
- Docstring: the operation's `summary` + `\n\n` + `description`, verbatim. If `summary` is absent (many operations declare only `description`), use the first sentence of `description` as the summary line and the remainder as the description body. If `description` is also absent, use `"<Method name in Title Case>."` as the summary (e.g., `"Retrieve."`) with no body.

### Example

```python
from __future__ import annotations

from blueticks._base_resource import BaseResource
from blueticks.types.account import Account


class AccountResource(BaseResource):
    def retrieve(self) -> Account:
        """Retrieve the authenticated account.

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

**Happy path.** Mock the transport to return a valid response body:
- If the OpenAPI operation's response schema includes an `example` field, use it verbatim.
- Otherwise, synthesize a minimal fixture covering every required field with plausible values (strings should be realistic, timestamps in ISO 8601 with `Z` suffix, IDs in the `<prefix>_<short>` convention used by Blueticks). Use at least one non-default value per non-ID field so the test verifies field-level parsing, not just that the object was constructed.

Assert the method returns the typed model with the expected field values.

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
