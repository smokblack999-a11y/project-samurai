import pytest

from app import queue

class FakeRedis:
    def __init__(self):
        self.calls = []
    async def xadd(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return "1-0"

@pytest.mark.asyncio
async def test_enqueue_does_not_trim_transport_stream(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(queue, "client", fake)
    await queue.enqueue({"id": "evt_1"})
    assert fake.calls == [((queue.STREAM, {"event": '{"id": "evt_1"}'}), {})]
