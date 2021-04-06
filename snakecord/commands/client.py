from functools import wraps
from ..client import Client
from .parsers import StringParser, FunctionArgParser
from ..events import EventPusher
from .commander import CommandInvokeEvent, CommandInvokeHandler
from .command import Command

from asyncio import get_event_loop, iscoroutine

class Commander(EventPusher):
    def __init__(self, loop=None):
        loop = loop or get_event_loop()
        super().__init__(loop)
        self.commands = {}

    def register_command(self, cmd):
        if cmd.name in self.commands:
            raise ValueError("This command is already registered.")
        self.commands[cmd.name] = cmd

class CommanderClient(Client):
    def __init__(self, prefix, *args, **kwargs):
        self.prefix = prefix
        super().__init__(*args, **kwargs)
        
        self.commander = Commander()
        self.register_listener('message_create', self._handle_message_create)

    async def _handle_message_create(self, evnt):
        message = evnt.message

        parser = StringParser(message.content)
        prefix = parser.buffer.read(len(self.prefix))
        event = CommandInvokeEvent(self.commander, message, parser, prefix)

        if prefix != self.prefix:
            return

        event.invoke()

    def command(self, name=None, **kwargs):
        def deco(func):
            nonlocal name
            name = name or func.__name__
            cmd = Command(self.commander, name, FunctionArgParser(func), **kwargs)
            self.commander.register_command(cmd)
            handler = self.commander._handlers.get(name)
            name = "invoke_{}".format(name)
            if handler is None:
                handler = self.commander._handlers[name] = CommandInvokeHandler(name)

            wrapped = self._wrap_callback(func)

            self.commander.register_listener(name, wrapped)
            return cmd
        return deco
    
    @staticmethod
    def _wrap_callback(func):
        @wraps(func)
        async def wrapped(handler):
            cmd = handler.evnt.command

            for guard in cmd.guards:
                await guard.check(handler.evnt)

            ret = func(handler.evnt, *handler.args, **handler.kwargs)

            if iscoroutine(ret):
                ret = await ret
            
            return ret
        return wrapped
