# blueticks — Python client for the Blueticks API

Official Python SDK for [Blueticks](https://blueticks.co).

## Install

```bash
pip install blueticks
```

## Quickstart

```python
from blueticks import Blueticks

client = Blueticks(api_key="bt_live_...")
ping = client.ping()
account = client.account.retrieve()
print(account.name)
```

See https://docs.blueticks.co for full documentation.
