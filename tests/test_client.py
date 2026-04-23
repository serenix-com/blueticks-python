from __future__ import annotations

import pytest

from blueticks import Blueticks
from blueticks._errors import BluetickError


def test_constructor_accepts_api_key() -> None:
    c = Blueticks(api_key="bt_live_x")
    assert c._api_key == "bt_live_x"
    c.close()


def test_constructor_falls_back_to_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BLUETICKS_API_KEY", "bt_test_env")
    c = Blueticks()
    assert c._api_key == "bt_test_env"
    c.close()


def test_constructor_raises_when_no_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BLUETICKS_API_KEY", raising=False)
    with pytest.raises(BluetickError) as info:
        Blueticks()
    assert "api_key" in str(info.value).lower() or "BLUETICKS_API_KEY" in str(info.value)


def test_base_url_env_var_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BLUETICKS_BASE_URL", "https://staging.example.test")
    c = Blueticks(api_key="k")
    assert c._base_url == "https://staging.example.test"
    c.close()


def test_explicit_base_url_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BLUETICKS_BASE_URL", "https://env.example.test")
    c = Blueticks(api_key="k", base_url="https://explicit.example.test")
    assert c._base_url == "https://explicit.example.test"
    c.close()


def test_context_manager_closes_transport() -> None:
    with Blueticks(api_key="k") as c:
        transport = c._transport
    assert transport._client.is_closed


def test_default_base_url() -> None:
    c = Blueticks(api_key="k")
    assert c._base_url == "https://api.blueticks.co"
    c.close()
