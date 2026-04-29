from blueticks.types.audiences import AppendContactsResult, Audience, Contact
from blueticks.types.campaigns import Campaign
from blueticks.types.messages import Message
from blueticks.types.webhooks import Webhook, WebhookCreateResult, WebhookEvent


def test_message_round_trip():
    data = {
        "id": "msg_1",
        "to": "+1",
        "from": None,
        "text": "hi",
        "media_url": None,
        "status": "queued",
        "send_at": None,
        "created_at": "2026-04-23T00:00:00Z",
        "sent_at": None,
        "delivered_at": None,
        "read_at": None,
        "failed_at": None,
        "failure_reason": None,
    }
    m = Message.model_validate(data)
    assert m.id == "msg_1"
    assert m.status == "queued"


def test_webhook_create_result_has_secret():
    data = {
        "id": "wh_1",
        "url": "https://a.com/",
        "events": ["message.delivered"],
        "description": None,
        "status": "enabled",
        "secret": "whsec_abc",
        "created_at": "2026-04-23T00:00:00Z",
    }
    wh = WebhookCreateResult.model_validate(data)
    assert wh.secret == "whsec_abc"


def test_webhook_list_item_hides_secret():
    data = {
        "id": "wh_1",
        "url": "https://a.com/",
        "events": ["message.delivered"],
        "description": None,
        "status": "enabled",
        "created_at": "2026-04-23T00:00:00Z",
    }
    wh = Webhook.model_validate(data)
    assert not hasattr(wh, "secret") or wh.secret is None  # type: ignore[union-attr]


def test_webhook_event_parses():
    data = {
        "id": "evt_1",
        "type": "message.delivered",
        "created_at": "2026-04-23T00:00:00Z",
        "data": {"id": "msg_1"},
    }
    ev = WebhookEvent.model_validate(data)
    assert ev.type == "message.delivered"
    assert ev.data["id"] == "msg_1"


def test_audience_and_contact():
    aud = Audience.model_validate(
        {
            "id": "aud_1",
            "name": "a",
            "contact_count": 2,
            "created_at": "2026-04-23T00:00:00Z",
        }
    )
    assert aud.contact_count == 2
    c = Contact.model_validate(
        {
            "id": "ctc_1",
            "to": "+1",
            "variables": {"name": "A"},
            "added_at": "2026-04-23T00:00:00Z",
        }
    )
    assert c.variables == {"name": "A"}


def test_append_contacts_result():
    r = AppendContactsResult.model_validate({"added": 3, "contact_count": 10})
    assert r.added == 3


def test_campaign_status_counters():
    c = Campaign.model_validate(
        {
            "id": "cmp_1",
            "name": "n",
            "audience_id": "aud_1",
            "status": "running",
            "total_count": 10,
            "sent_count": 5,
            "delivered_count": 3,
            "read_count": 1,
            "failed_count": 0,
            "from": None,
            "created_at": "2026-04-23T00:00:00Z",
            "started_at": "2026-04-23T00:00:00Z",
            "completed_at": None,
            "aborted_at": None,
        }
    )
    assert c.status == "running"
    assert c.sent_count == 5
