from .exceptions import InvokeGuardFailure
from ..utils import undefined
from asyncio import iscoroutine


WHITESPACE = (' ', '\t', '\r', '\n')

class InvokeGuard:
    def __init__(self, func):
        self.func = func
    
    async def _can_run(self, evnt):
        try:
            ret = await self._run_func(evnt)
            evnt.exception = None
            return ret
        except Exception as e:
            evnt.exception = e
            return False
    
    async def _run_func(self, *args, **kwargs):
        ret = self.func(*args, **kwargs)
        if iscoroutine(ret):
            ret = await ret
        return ret
    
    async def check(self, evnt):
        can_run = await self._can_run(evnt)
        if not can_run:
            raise InvokeGuardFailure("Check {.__name__} failed.".format(self.func)) from evnt.exception

invoke_guard = InvokeGuard # Actually looks like a decorator

class Command:
    def __init__(self, commander, name, args, *, description=None, overflow=False, aliases=None, guards=None):
        self.commander = commander
        self.name = name
        self.description = description
        self.aliases = [] if aliases is None else list(aliases)
        self.guards = [] if guards is None else list(guards)

        self.vararg = args.vararg
        self.varkwargs = args.varkwarg

        assert not (self.vararg and overflow), "can't have variadic positional argument with overflow"

        if overflow:
            self.overflow = args.kw_only.pop()
        else:
            self.overflow = None

        self.flags = {arg.name: arg for arg in args.kw_only}
        self.args = {arg.name: arg for arg in (args.pos_only + args.pos_or_kw)[1:]}

    def _parse_args(self, evnt):
        parser = evnt.parser

        args = []

        while True:
            position = parser.buffer.tell()
            try:
                char = parser.get()
            except EOFError:
                break
            if char == '-':
                name = parser.read_until(('=', *WHITESPACE), '').strip()
                if not self.varkwargs and name not in self.flags:
                    parser.buffer.seek(position)
                else:
                    value = parser.get_argument()
                    evnt.kwargs[name] = value
                    continue
            elif char in WHITESPACE:
                continue
            else:
                parser.buffer.seek(position)

            if not self.vararg and len(args) == len(self.args):
                break

            args.append(parser.get_argument())

        if not self.vararg:
            for arg in self.args.values():
                try:
                    evnt.args.append(args.pop(0))
                except IndexError:
                    if arg.optional:
                        default = None if arg.default is not undefined else arg.default
                        args.append(default)
                    else:
                        raise
        else:
            evnt.args.extend(args)

        if self.overflow is not None:
            evnt.kwargs[self.overflow.name] = parser.buffer.read()

    def invoke(self, evnt):
        self._parse_args(evnt)
        self.commander.push_event('invoke_{}'.format(self.name), evnt, *evnt.args, **evnt.kwargs)

    def add_alias(self, alias):
        if not isinstance(alias, str):
            raise ValueError("Alias must be a str.")
        elif alias in self.aliases:
            raise ValueError("This is already an existing alias.")
        try:
            self.aliases.append(alias)
        except AttributeError:
            if hasattr(self, 'aliases'):
                raise ValueError("Aliases is not a list.") from None
            raise
        
