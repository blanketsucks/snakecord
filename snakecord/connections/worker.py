from __future__ import annotations

import enum
import select
import socket
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..manager import BaseManager


class WorkerOpcode(enum.IntEnum):
    WAKEUP = 0
    SHUTDOWN = 1


class ConnectionWorker(threading.Thread):
    def __init__(self, manager: BaseManager):
        super().__init__(daemon=True)

        self.manager = manager
        self.shutting_down = False

        self._rsock, self._wsock = socket.socketpair()
        self._rsock.setblocking(False)
        self._wsock.setblocking(False)

    async def wakeup(self):
        await self.manager.loop.sock_sendall(
            self._wsock, bytes((WorkerOpcode.WAKEUP,)))

    async def shutdown(self):
        await self.manager.loop.sock_sendall(
            self._wsock, bytes((WorkerOpcode.SHUTDOWN,)))

    def run(self):
        while not self.shutting_down:
            timeout = None
            rlist = [self._rsock.fileno()]
            wlist = []

            for fd, conn in self.manager.connections.items():
                next_beat = conn.calcbeat()
                if next_beat is None:
                    continue

                if next_beat <= 0:
                    wlist.append(fd)

                if timeout is None or next_beat < timeout:
                    timeout = abs(next_beat)

            rready, wready, _ = select.select(
                rlist, wlist, [], timeout)

            if rready:
                while True:
                    try:
                        opcode = self._rsock.recv(1)

                        if opcode == WorkerOpcode.SHUTDOWN:
                            self.shutting_down = True
                    except BlockingIOError:
                        break

            for fd in wready:
                conn = self.manager.connections[fd]
                conn.send_heartbeat()
