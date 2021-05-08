import enum
import json
import platform
import time

from wsaio import WebSocketFrame, WebSocketOpcode, taskify

from .base import BaseConnection, WebSocketMessage


class ShardOpcode(enum.IntEnum):
    DISPATCH = 0  # Discord -> Shard
    HEARTBEAT = 1  # Discord <-> Shard
    IDENTIFY = 2  # Discord <- Shard
    PRESENCE_UPDATE = 3  # Discord -> Shard
    VOICE_STATE_UPDATE = 4  # Discord -> Shard
    VOICE_SERVER_PING = 5  # Discord ~ Shard
    RESUME = 6  # Discord <- Shard
    RECONNECT = 7  # Discord -> Shard
    REQUEST_GUILD_MEMBERS = 8  # Discord <- Shard
    INVALID_SESSION = 9  # Discord -> Shard
    HELLO = 10  # Discord -> Shard
    HEARTBEAT_ACK = 11  # Discord -> Shard


class Shard(BaseConnection):
    HEARTBEAT_PAYLOAD = WebSocketFrame(
        opcode=WebSocketOpcode.TEXT,
        data=json.dumps({
            'op': ShardOpcode.HEARTBEAT,
            'd': None
        }).encode()
    ).encode(masked=True)

    ENDPOINT = 'wss://gateway.discord.gg?v=8'

    async def identify(self):
        payload = {
            'op': ShardOpcode.IDENTIFY,
            'd': {
                'token': self.manager.token,
                'intents': self.manager.intents,
                'properties': {
                    '$os': platform.system(),
                    '$browser': 'snakecord',
                    '$device': 'snakecord'
                }
            }
        }
        await self.send_json(payload)

    @taskify
    async def ws_text_received(self, data):
        msg = WebSocketMessage.unmarshal(data)

        if msg.opcode == ShardOpcode.DISPATCH:
            self.manager.dispatch(msg.event_name, self, msg.data)

        elif msg.opcode == ShardOpcode.HELLO:
            self.heartbeat_interval = (
                msg.data['heartbeat_interval'] / 1000
            )
            await self.manager.connection_worker.wakeup()
            await self.identify()

        elif msg.opcode == ShardOpcode.HEARTBEAT:
            self.send_heartbeat()

        elif msg.opcode == ShardOpcode.HEARTBEAT_ACK:
            self.heartbeats_acked += 1
            self.heartbeat_last_acked = time.perf_counter()
            await self.manager.connection_worker.wakeup()

    async def connect(self, *args, **kwargs):
        await super().connect(self.ENDPOINT, *args, **kwargs)
