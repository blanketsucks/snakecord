from __future__ import annotations

import asyncio
import functools
from numbers import Number
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple
from weakref import WeakSet

__all__ = ('EventNamespace', 'EventWaiter', 'EventDispatcher',
           'EventDefinition')


class EventDefinition:
    """An empty class that merely marks subclasses as being an event."""


class EventNamespace:
    """A class that gathers :class:`EventDefinition` s and stores
    them in :attr:`EventNamespace.__events__` when subclassed.

    Attributes
        __events__: dict[str, EventDefinition]
            The :class:`EventDefinition` s defined in the class.
    """
    __events__: Dict[str, EventDefinition] = {}

    def __init_subclass__(cls):
        cls.__events__ = {}

        for base in cls.__bases__:
            if issubclass(base, EventNamespace):
                cls.__events__.update(base.__events__)

        for name, attr in cls.__dict__.items():
            if isinstance(attr, type) and issubclass(attr, EventDefinition):
                cls.__events__[name] = attr


class EventWaiter:
    """A class that receives events from an :class:`EventDispatcher`
    if the event passes the filter.

    Attributes
        name: str
            The name of the event that the waiter will receive.

        dispatcher: EventDispatcher
            The :class:`EventDispatcher` that the waiter is
            receiving events from.

        timeout: Optional[Number]
            The maximum amount of time to wait for an event to
            be received, :exc:`asyncio.TimeoutError` is raised
            when this timeout is exceeded.

        filterer: Optional[Callable[..., bool]]
            A callable that determines if the event is wanted.

            Example::

                if filterer(event):
                    return event

    .. note::
        This class shouldn't be created directly,
        use :meth:`EventDispatcher.wait` instead.
    """
    def __init__(self, name: str, dispatcher: EventDispatcher,
                 timeout: Optional[Number],
                 filterer: Optional[Callable[..., bool]]) -> None:
        self.name = name
        self.dispatcher = dispatcher
        self.timeout = timeout
        self.filterer = filterer
        self.waiting = False
        self._queue: asyncio.Queue[Tuple[Any, ...]] = asyncio.Queue()

    def _put(self, value: Tuple[Any, ...]) -> None:
        if self.filterer is not None:
            if not self.filterer(*value):
                return

        self._queue.put_nowait(value)

    async def _get(self) -> Any:
        if self.waiting:
            raise RuntimeError('Can\'t concurrently wait on waiter')

        self.waiting = True

        value = await asyncio.wait_for(self._queue.get(), timeout=self.timeout)
        if len(value) == 1:
            value, = value

        self.waiting = False

        return value

    def __aiter__(self) -> EventWaiter:
        return self

    async def __anext__(self) -> Any:
        return await self._get()

    async def __await__impl(self) -> None:
        try:
            return await self._get()
        finally:
            self.close()

    def __await__(self):
        return self.__await__impl().__await__()

    def close(self) -> None:
        """Closes the waiter and removes it from the
        corresponding :class:`EventDispatcher`, any coroutines
        waiting on it will receive an :exc:`asyncio.CancelledError`.
        """
        # if self._future is not None:
        #     try:
        #         self._future.cancel()
        #     except asyncio.InvalidStateError:
        #         pass
        try:
            self.dispatcher.remove_waiter(self)
        except KeyError:
            pass

    __del__ = close


def ensure_future(coro: Awaitable) -> Optional[asyncio.Future]:
    if hasattr(coro.__class__, '__await__'):
        return asyncio.ensure_future(coro)
    return None


class EventDispatcher:
    """A class dedicated to callbacks, similar to
    Node.js's `EventEmitter`.

    Attributes
        events: EventNamespace
            The events to use.

        loop: Optional[asyncio.AbstractEventLoop]
            The event loop that is... not used,
            but is useful for subclasses.

    Example::

        class Events(EventNamespace):

            class some_event(EventDefinition):
                def __init__(self, dispatcher, abc):
                    self.dispatcher = dispatcher
                    self.abc = abc


        class Dispatcher(EventDispatcher):
            events = Events

            ...

        dispatcher = Dispatcher()


        @dispatcher.on()
        def some_event(evnt: Events.some_event) -> None:
            print(f'Received some_event {evnt.abc=}')


        dispatcher.dispatch('some_event', 10)

    .. note::
        Event names are case insensitive
    """
    events: EventNamespace

    def __init__(self, *,
                 loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self._listeners: Dict[str, List[Callable]] = {}
        self._waiters: Dict[str, WeakSet] = {}
        self._subscribers: List[EventDispatcher] = []

    def register_listener(self, name: str,
                          callback: Callable[..., Any]) -> None:
        """Registers `callback` to be called when an event
        with the same name is dispatched.

        Arguments
            name: str
                The name of the event to listen for.

            callback: Callable[..., Any]
                The callback.
        """
        listeners = self._listeners.setdefault(name.lower(), [])
        listeners.append(callback)

    def remove_listener(self, name: str, callback: Callable[..., Any]) -> None:
        """Unregisters `callback` from being called when an event
        with the same name is dispatched.

        Arguments
            name: str
                The name of the event that was being listened for.

            callback: Callable[..., Any]
                The callback.
        """
        listeners = self._listeners.get(name.lower())
        if listeners is not None:
            listeners.remove(callback)

    def register_waiter(self, name: str, *,
                        timeout: Optional[Number] = None,
                        filterer: Callable[..., Any] = None) -> EventWaiter:
        """Registers a new waiter, see :class:`EventWaiter`
        for information amout arguments.

        Returns
            :class:`EventWaiter`
                The waiter.

        Examples
            Using in an `async-for` loop::

                async for evnt in dispatcher.wait('hello_world'):
                    print(evnt)

            Using in an `await` statement::

                evnt = await dispatcher.wait('hello_world',
                                             filterer=lambda evnt: 2 + 2 == 4)
        """
        waiters = self._waiters.setdefault(name.lower(), WeakSet())
        waiter = EventWaiter(name, self, timeout, filterer)
        waiters.add(waiter)
        return waiter

    wait = register_waiter

    def remove_waiter(self, waiter: EventWaiter) -> None:
        """Unregisters `waiter`, the waiter will stop receiving
        events after this method is called. Consider using
        :meth:`EventWaiter.close` if you'd like to notify
        awaiting coroutines.
        """
        waiters = self._waiters.get(waiter.name.lower())
        if waiters is not None:
            waiters.remove(waiter)

    def run_callbacks(self, name: str, *args: Any) -> None:
        r"""Runs listeners and waiters that are listening for `name`
        and recursively calls the same method for all subscribed
        dispatchers.

        Arguments
            name: str
                The name of the event.

            \*args: Any
                The arguments to pass to callbacks.
        """
        name = name.lower()
        listeners = self._listeners.get(name)
        waiters = self._waiters.get(name)

        if listeners is not None:
            for listener in listeners:
                ensure_future(listener(*args))

        if waiters is not None:
            for waiter in waiters:
                waiter._put(args)

        for subscriber in self._subscribers:
            subscriber.run_callbacks(name, *args)

    def dispatch(self, name: str, *args) -> None:
        """Same as :meth:`EventDispatcher.dispatch` but looks
        through :attr:`EventDispatcher.events` for the event
        class and replaces the args with an instance of it
        created with the original args.
        """
        event = self.events.__events__.get(name.lower())

        if event is not None:
            args = (event(self, *args),)

        self.run_callbacks(name, *args)

    def subscribe(self, dispatcher: EventDispatcher):
        """Subscribes to another dispatcher causing it to
        receive all events dispatched to the other dispatcher.

        Arguments
            dispatcher: EventDispatcher
                The dispatcher to subscribe to.
        """
        dispatcher._subscribers.append(self)

    def unsubscribe(self, dispatcher: EventDispatcher):
        """Unsubscribes from another dispatcher causing it to
        stop receiving events dispatched to the other dispatcher.

        Arguments
            dispatcher: EventDispatcher
                The dispatcher to unsubscribe from.
        """
        dispatcher._subscribers.remove(self)

    def on(self, name: Optional[str] = None):
        """This is :meth:`EventDispatcher.register_listener` but in
        decorator form.

        Arguments
            name: Optional[str]
                The name of the event to listen for, if None is provided
                then the name of the function is used.
        """
        def wrapped(func: Callable[..., Any]):
            self.register_listener(name or func.__name__, func)
            return func
        return wrapped

    def once(self, name: Optional[str] = None):
        """This is similar to :meth:`EventDispatcher.on` but removes
        the listener the first time the event is dispatched.
        """
        def wrapped(func):
            nonlocal name
            name = (name or func.__name__).lower()

            @functools.wraps(func)
            def callback(*args):
                ensure_future(func, *args)
                self.remove_listener(name, callback)

            self.remove_listener(name, callback)

            return func
        return wrapped
