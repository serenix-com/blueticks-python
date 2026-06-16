from blueticks.types.audiences import AppendContactsResult, Audience, Contact
from blueticks.types.campaigns import Campaign
from blueticks.types.scheduled_messages import ScheduledMessage
from blueticks.types.webhooks import Webhook, WebhookCreateResult, WebhookEvent


def test_scheduled_message_round_trip():
    data = {
        "id": "msg_1",
        "to": "+1",
        "from": None,
        "type": "text",
        "text": "hi",
        "mediaUrl": None,
        "status": "pending",
        "sendAt": None,
        "createdAt": "2026-04-23T00:00:00Z",
        "confirmedAt": None,
        "receivedAt": None,
        "readAt": None,
        "playedAt": None,
        "failedAt": None,
        "failureReason": None,
    }
    m = ScheduledMessage.model_validate(data)
    assert m.id == "msg_1"
    assert m.status == "pending"
    assert m.type == "text"


def test_webhook_create_result_has_secret():
    data = {
        "id": "wh_1",
        "url": "https://a.com/",
        "events": ["message.delivered"],
        "description": None,
        "status": "enabled",
        "secret": "whsec_abc",
        "createdAt": "2026-04-23T00:00:00Z",
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
        "createdAt": "2026-04-23T00:00:00Z",
    }
    wh = Webhook.model_validate(data)
    assert not hasattr(wh, "secret") or wh.secret is None  # type: ignore[union-attr]


def test_webhook_event_parses():
    data = {
        "id": "evt_1",
        "type": "message.delivered",
        "createdAt": "2026-04-23T00:00:00Z",
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
            "contactCount": 2,
            "createdAt": "2026-04-23T00:00:00Z",
        }
    )
    assert aud.contact_count == 2
    c = Contact.model_validate(
        {
            "id": "ctc_1",
            "to": "+1",
            "variables": {"name": "A"},
            "addedAt": "2026-04-23T00:00:00Z",
        }
    )
    assert c.variables == {"name": "A"}


def test_append_contacts_result():
    r = AppendContactsResult.model_validate({"added": 3, "contactCount": 10})
    assert r.added == 3


def test_campaign_status_counters():
    c = Campaign.model_validate(
        {
            "id": "cmp_1",
            "name": "n",
            "audienceId": "aud_1",
            "status": "running",
            "totalCount": 10,
            "sentCount": 5,
            "deliveredCount": 3,
            "readCount": 1,
            "failedCount": 0,
            "from": None,
            "createdAt": "2026-04-23T00:00:00Z",
            "startedAt": "2026-04-23T00:00:00Z",
            "completedAt": None,
            "abortedAt": None,
        }
    )
    assert c.status == "running"
    assert c.sent_count == 5
