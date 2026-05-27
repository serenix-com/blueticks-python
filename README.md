# blueticks — Python client for the Blueticks API

Official Python SDK for [Blueticks](https://blueticks.co).

## Install

```bash
pip install blueticks
```

## Quickstart

```python
from blueticks import Blueticks

client = Blueticks(api_key="BLUETICKS_API_KEY")
ping = client.ping()
account = client.account.retrieve()
print(account.name)
```

See https://docs.blueticks.co for full documentation.

## Migrating from 3.x → 4.0

The backend renamed the queued-send domain on the wire: `POST/GET/PATCH /v1/messages*` → `POST/GET/PATCH /v1/scheduled-messages*`. To match, the SDK has dropped the `client.messages` resource and moved every queued-send method onto `client.scheduled_messages`. The legacy `client.messages.send(...)` is renamed to `client.scheduled_messages.create(...)`.

```python
# Before (3.x)
client.messages.send(to="+1...", type="text", text="hi")
client.messages.retrieve("msg_1")
client.messages.list()
client.messages.update("msg_1", text="edited")

# After (4.0)
client.scheduled_messages.create(to="+1...", type="text", text="hi")
client.scheduled_messages.retrieve("msg_1")
client.scheduled_messages.list()
client.scheduled_messages.update("msg_1", text="edited")
```

The response type was likewise renamed `Message` → `ScheduledMessage` (same fields). Import from `blueticks.types.scheduled_messages` instead of `blueticks.types.messages`.
