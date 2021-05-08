from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..manager import BaseManager

from wsaio import WebSocketClient

from ..utils import JsonField, JsonTemplate


WebSocketMessage = JsonTemplate(
    opcode=JsonField('op'),
    data=JsonField('d'),
    sequence=JsonField('s'),
    event_name=JsonField('t'),
).default_object()


class BaseConnection(WebSocketClient):
    HEARTBEAT_PAYLOAD: bytes

    def __init__(self, manager: BaseManager):
        super().__init__(loop=manager.loop)

        self.manager = manager
        self.heartbeats_sent = 0
        self.heartbeats_acked = 0
        self.heartbeat_interval = float('inf')
        self.heartbeat_last_sent = float('inf')
        self.heartbeat_last_acked = float('inf')

    @property
    def latency(self):
        return self.heartbeat_last_acked - self.heartbeat_last_sent

    def calcbeat(self):
        if self.heartbeat_interval == float('inf'):
            return None

        if self.heartbeats_sent != self.heartbeats_acked:
            return None

        if self.heartbeats_sent == 0:
            return 0

        return (self.heartbeat_last_acked
                + self.heartbeat_interval
                - time.perf_counter())

    def send_heartbeat(self):
        self.transport.write(self.HEARTBEAT_PAYLOAD)
        self.heartbeats_sent += 1
        self.heartbeat_last_sent = time.perf_counter()

    async def send_json(self, data, *args, **kwargs):
        await self.send_str(json.dumps(data), *args, **kwargs)
