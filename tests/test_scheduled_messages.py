from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types._deleted_resource import DeletedResource
from blueticks.types.page import Page
from blueticks.types.scheduled_messages import ScheduledMessage


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def _page(items, **extra):
    body = {"success": True, "data": items, "limit": 50, "skip": 0, "total": len(items)}
    body.update(extra)
    return httpx.Response(200, json=body)


def _scheduled(sid="msg_1", **overrides):
    data = {
        "id": sid,
        "waMessageKey": None,
        "to": "12345@c.us",
        "type": "text",
        "text": "hello",
        "mediaUrl": None,
        "mediaKind": None,
        "pollQuestion": None,
        "pollOptions": None,
        "pollAllowMultiple": None,
        "status": "pending",
        "sendAt": None,
        "createdAt": "2026-04-23T00:00:00Z",
        "confirmedAt": None,
        "failureReason": None,
        "linkPreview": None,
    }
    data.update(overrides)
    return data


def test_list_scheduled_messages_passes_camel_case_params():
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        assert req.url.path == "/v1/scheduled-messages"
        return _page([_scheduled("msg_1"), _scheduled("msg_2", status="delivered")])

    page = _client(handler).scheduled_messages.list(
        chat_id="12345@c.us", search_token="hi", status="pending", order="desc", skip=0, limit=25
    )
    assert isinstance(page, Page)
    assert page.data[1].status == "delivered"
    assert params_seen == {
        "chatId": "12345@c.us",
        "searchToken": "hi",
        "status": "pending",
        "order": "desc",
        "skip": "0",
        "limit": "25",
    }


def test_create_posts_to_chat_scoped_path():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/scheduled-messages/12345@c.us"
        return _ok(_scheduled("msg_1", status="pending", sendAt="2026-05-01T09:00:00Z"), status=201)

    m = _client(handler).scheduled_messages.create(
        "12345@c.us",
        type="text",
        text="hello",
        send_at="2026-05-01T09:00:00Z",
        reply_to="wamid.prev",
    )
    assert isinstance(m, ScheduledMessage)
    assert m.status == "pending"
    assert m.send_at is not None
    assert body_seen == {
        "type": "text",
        "text": "hello",
        "sendAt": "2026-05-01T09:00:00Z",
        "replyTo": "wamid.prev",
    }


def test_create_poll_serializes_camel_case():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return _ok(_scheduled("msg_2", type="poll", text=None, pollQuestion="Pizza?"), status=201)

    m = _client(handler).scheduled_messages.create(
        "12345@c.us",
        type="poll",
        poll_question="Pizza?",
        poll_options=["Yes", "No"],
        poll_allow_multiple=False,
    )
    assert m.type == "poll"
    assert m.poll_question == "Pizza?"
    assert body_seen == {
        "type": "poll",
        "pollQuestion": "Pizza?",
        "pollOptions": ["Yes", "No"],
        "pollAllowMultiple": False,
    }


def test_create_with_idempotency_key_sets_header():
    headers_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        headers_seen.update(dict(req.headers))
        return _ok(_scheduled("msg_5"), status=201)

    _client(handler).scheduled_messages.create(
        "12345@c.us", type="text", text="hi", idempotency_key="key-abc"
    )
    assert headers_seen["idempotency-key"] == "key-abc"


def test_retrieve_scheduled_message():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/scheduled-messages/msg_xyz"
        return _ok(_scheduled("msg_xyz", status="delivered", confirmedAt="2026-04-23T00:00:02Z"))

    m = _client(handler).scheduled_messages.retrieve("msg_xyz")
    assert m.status == "delivered"
    assert m.confirmed_at is not None


def test_update_serializes_camel_case():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PATCH"
        assert req.url.path == "/v1/scheduled-messages/msg_xyz"
        return _ok(_scheduled("msg_xyz", text="edited"))

    result = _client(handler).scheduled_messages.update(
        "msg_xyz", text="edited", media_url="https://cdn.example/x.jpg"
    )
    assert result.text == "edited"
    assert body_seen == {"text": "edited", "mediaUrl": "https://cdn.example/x.jpg"}


def test_delete_scheduled_message():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/scheduled-messages/msg_xyz"
        return _ok({"id": "msg_xyz", "deleted": True})

    result = _client(handler).scheduled_messages.delete("msg_xyz")
    assert isinstance(result, DeletedResource)
    assert result.id == "msg_xyz"
    assert result.deleted is True


def test_scheduled_messages_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_sm_1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).scheduled_messages.retrieve("msg_1")
    assert exc_info.value.request_id == "req_sm_1"


def test_scheduled_message_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).scheduled_messages.retrieve("msg_1")


def test_create_scheduled_message_with_mentions_and_recipient_name():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return httpx.Response(201, json={"success": True, "data": _scheduled()})

    _client(handler).scheduled_messages.create(
        "123@g.us",
        type="text",
        text="hi @Dana",
        mentions=["14155551234@c.us"],
        recipient_name="Team chat",
    )
    assert body_seen == {
        "type": "text",
        "text": "hi @Dana",
        "mentions": ["14155551234@c.us"],
        "recipientName": "Team chat",
    }


def test_update_scheduled_message_with_mentions():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return httpx.Response(200, json={"success": True, "data": _scheduled()})

    _client(handler).scheduled_messages.update("sm_1", mentions=["14155551234@c.us"])
    assert body_seen == {"mentions": ["14155551234@c.us"]}


def test_list_scheduled_messages_forwards_include_flags():
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        return _page([_scheduled()])

    _client(handler).scheduled_messages.list(
        chat_id="12345@c.us", include_sent=True, include_preview=False
    )
    assert params_seen == {
        "chatId": "12345@c.us",
        "includeSent": "true",
        "includePreview": "false",
    }


def test_create_scheduled_message_with_recurrence_labels_and_from():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return httpx.Response(201, json={"success": True, "data": _scheduled()})

    recurrence = {
        "frequency": "weekly",
        "interval": 1,
        "byWeekday": ["MO", "FR"],
        "endsAfter": 10,
    }
    _client(handler).scheduled_messages.create(
        "12345@c.us",
        type="text",
        text="standup",
        send_at="2026-12-01T09:00:00+02:00",
        recurrence=recurrence,
        wa_label_ids=["7"],
        from_="+14155550000",
        media_file_id="Ab12Cd34Ef56",
        media_mime_type="image/png",
        button_reply={"replyTo": "false_12345@c.us_X", "rowId": "r1"},
    )
    assert body_seen == {
        "type": "text",
        "text": "standup",
        "sendAt": "2026-12-01T09:00:00+02:00",
        "recurrence": recurrence,
        "waLabelIds": ["7"],
        "from": "+14155550000",
        "mediaFileId": "Ab12Cd34Ef56",
        "mediaMimeType": "image/png",
        "buttonReply": {"replyTo": "false_12345@c.us_X", "rowId": "r1"},
    }


def test_create_scheduled_message_omits_type_when_not_given():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return httpx.Response(201, json={"success": True, "data": _scheduled()})

    _client(handler).scheduled_messages.create("12345@c.us", text="hi")
    assert "type" not in body_seen


def test_update_scheduled_message_media_file_id_and_mime():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return _ok(_scheduled())

    _client(handler).scheduled_messages.update(
        "msg_1", media_file_id="Ab12Cd34Ef56", media_mime_type="application/pdf"
    )
    assert body_seen == {"mediaFileId": "Ab12Cd34Ef56", "mediaMimeType": "application/pdf"}


def test_cancel_scheduled_message_posts_to_cancel_path():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/scheduled-messages/msg_1/cancel"
        return _ok(_scheduled(status="cancelled"))

    result = _client(handler).scheduled_messages.cancel("msg_1")
    assert isinstance(result, ScheduledMessage)
    assert result.status == "cancelled"


def test_scheduled_message_parses_recurrence_warning_and_wa_labels():
    data = _scheduled(
        recipientName="Acme Ops",
        recurrence={
            "frequency": "monthly",
            "interval": 2,
            "byWeekday": None,
            "endsAfter": 5,
            "endsOn": None,
            "timezone": "Europe/Berlin",
        },
        waLabels={"requested": 1, "applied": False, "error": "wa_business_required"},
        warning={"code": "no_engine_connected", "message": "No engine was online."},
    )
    result = _client(lambda req: _ok(data)).scheduled_messages.retrieve("msg_1")
    assert result.recipient_name == "Acme Ops"
    assert result.recurrence is not None
    assert result.recurrence.frequency == "monthly"
    assert result.recurrence.interval == 2
    assert result.recurrence.timezone == "Europe/Berlin"
    assert result.wa_labels is not None
    assert result.wa_labels.error == "wa_business_required"
    assert result.warning is not None
    assert result.warning.code == "no_engine_connected"
