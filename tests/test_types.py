from __future__ import annotations

from blueticks.types.audiences import AudienceContact
from blueticks.types.campaigns import Campaign
from blueticks.types.messages import Message
from blueticks.types.page import Page
from blueticks.types.scheduled_messages import ScheduledMessage, WaMessageKey
from blueticks.types.webhooks import Webhook, WebhookEvent


def test_camel_case_aliases_parse_from_wire():
    """Response models accept the API's camelCase JSON via alias_generator."""
    c = Campaign.model_validate(
        {
            "cmpId": "cmp_1",
            "name": "n",
            "audienceId": "aud_1",
            "status": "running",
            "totalCount": 10,
            "sentCount": 5,
            "deliveredCount": 3,
            "readCount": 1,
            "failedCount": 0,
            "createdAt": "2026-04-23T00:00:00Z",
            "startedAt": "2026-04-23T00:00:00Z",
        }
    )
    assert c.cmp_id == "cmp_1"
    assert c.audience_id == "aud_1"
    assert c.status == "running"
    assert c.sent_count == 5
    assert c.started_at is not None


def test_wa_message_key_serialized_and_from_me_aliases():
    key = WaMessageKey.model_validate(
        {"fromMe": True, "remote": "1@c.us", "id": "X", "_serialized": "true_1@c.us_X"}
    )
    assert key.from_me is True
    assert key.serialized == "true_1@c.us_X"


def test_message_from_reserved_keyword_alias():
    m = Message.model_validate(
        {
            "waMessageKey": {"fromMe": False},
            "chatId": "1@c.us",
            "from": "1@c.us",
            "type": "chat",
            "fromMe": False,
        }
    )
    assert m.from_ == "1@c.us"
    assert m.wa_message_key.from_me is False


def test_scheduled_message_direct_send_shape_has_null_id():
    m = ScheduledMessage.model_validate(
        {
            "id": None,
            "waMessageKey": {"fromMe": True, "id": "X"},
            "to": "1@c.us",
            "type": "text",
            "status": "sent",
            "createdAt": "2026-04-23T00:00:00Z",
        }
    )
    assert m.id is None
    assert m.status == "sent"
    assert m.wa_message_key is not None


def test_audience_contact_variables_dict():
    c = AudienceContact.model_validate(
        {"id": "ctc_1", "to": "+1", "variables": {"name": "A"}, "addedAt": "2026-04-23T00:00:00Z"}
    )
    assert c.variables == {"name": "A"}
    assert c.added_at.year == 2026


def test_offset_page_parses_pagination_metadata():
    page = Page[Webhook].model_validate(
        {
            "success": True,
            "data": [
                {
                    "id": "wh_1",
                    "url": "https://a.com/",
                    "events": ["message.delivered"],
                    "status": "enabled",
                    "createdAt": "2026-04-23T00:00:00Z",
                }
            ],
            "limit": 50,
            "skip": 0,
            "total": 1,
        }
    )
    assert page.limit == 50
    assert page.skip == 0
    assert page.total == 1
    assert page.has_more is None
    assert page.data[0].id == "wh_1"


def test_webhook_event_parses_snake_case_payload():
    ev = WebhookEvent.model_validate(
        {
            "id": "evt_1",
            "type": "message.delivered",
            "created_at": "2026-04-23T00:00:00Z",
            "data": {"id": "msg_1"},
        }
    )
    assert ev.type == "message.delivered"
    assert ev.data["id"] == "msg_1"
