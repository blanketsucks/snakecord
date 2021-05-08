from __future__ import annotations

import weakref
from typing import Iterable, TYPE_CHECKING

from ..utils.snowflake import Snowflake

if TYPE_CHECKING:
    from ..manager import BaseManager


class BaseMapping:
    def __iter__(self):
        return iter(list(self.values()))

    def __reversed__(self):
        return reversed(list(self.items()))

    @classmethod
    def for_type(cls, klass):
        return type('Mapping', (cls, klass), {})


class BaseSnowflakeMapping(BaseMapping):
    def __setitem__(self, key, value):
        return super().__setitem__(Snowflake.try_snowflake(key), value)

    def __getitem__(self, key):
        return super().__getitem__(Snowflake.try_snowflake(key))

    def __delitem__(self, key):
        return super().__delitem__(Snowflake.try_snowflake(key))

    def __contains__(self, key) -> bool:
        return Snowflake.try_snowflake(key) in self

    def get(self, key, default=None):
        return super().get(Snowflake.try_snowflake(key), default)

    def pop(self, key, *args, **kwargs):
        return super().pop(Snowflake.try_snowflake(key), *args, **kwargs)


Mapping = BaseMapping.for_type(dict)
SnowflakeMapping = BaseSnowflakeMapping.for_type(dict)
WeakValueMapping = BaseMapping.for_type(weakref.WeakValueDictionary)
WeakValueSnowflakeMapping = (
    SnowflakeMapping.for_type(weakref.WeakValueDictionary)
)


class BaseState:
    __container__ = Mapping
    __recycled_container__ = WeakValueMapping
    __maxsize__ = 0
    __replace__ = True

    def __init__(self, *, manager: BaseManager) -> None:
        self._items: BaseMapping = self.__container__()
        self._recycle_bin: BaseMapping = self.__recycled_container__()
        self.manager = manager

    def __repr__(self) -> str:
        return (f'<{self.__class__.__name__} length={len(self)},'
                f' recycled={len(self._recycle_bin)}>')

    @classmethod
    def set_maxsize(cls, maxsize: int) -> None:
        cls.__maxsize__ = maxsize

    @classmethod
    def set_replace(cls, replace: bool) -> None:
        cls.__replace__ = replace

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return self._items.__iter__()

    def __reversed__(self):
        return self._items.__reversed__()

    def set(self, key, value):
        if self.__maxsize__ < 0:
            return False

        if (
            self.__maxsize__ != 0
            and len(self) >= self.__maxsize__
        ):
            if not self.__replace__:
                return False

            self.popitem().uncache()

        self._items.__setitem__(key, value)
        return True

    __setitem__ = set

    def __getitem__(self, key):
        return self._items.__getitem__(key)

    def __delitem__(self, key):
        return self._items.__delitem__(key)

    def __contains__(self, key):
        return self._items.__contains__(key)

    def keys(self):
        return self._items.keys()

    def items(self):
        return self._items.items()

    def values(self):
        return self._items.values()

    def recycle(self, key, value):
        self._recycle_bin[key] = value

    def unrecycle(self, *args, **kwargs):
        return self._recycle_bin.pop(*args, **kwargs)

    def get(self, *args, **kwargs):
        return (self._recycle_bin.get(*args, **kwargs)
                or self._items.get(*args, **kwargs))

    def pop(self, *args, **kwargs):
        return self._items.pop(*args, **kwargs)

    def popitem(self, *args, **kwargs):
        self._items.popitem(*args, **kwargs)

    def find(self, func):
        for item in self:
            if func(item):
                return item

    def append(self, data: dict):
        raise NotImplementedError

    def extend(self, data: Iterable[dict]) -> list:
        return [self.append(d) for d in data]


class BaseSubState:
    def __init__(self, *, superstate: BaseState) -> None:
        self.superstate = superstate

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} length={len(self)}>'

    def __related__(self, item) -> bool:
        raise NotImplementedError

    def __len__(self):
        return sum(1 for _ in self)

    def __iter__(self):
        for item in self.superstate:
            if self.__related__(item):
                yield item

    def __reversed__(self):
        for item in reversed(self.superstate):
            if self.__related__(item):
                yield item

    def __getitem__(self, key):
        item = self.superstate.__getitem__(key)
        if not self.__related__(item):
            raise KeyError(key)
        return item

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        return True

    def get(self, key, default=None):
        item = self.superstate.get(key, default)
        if not self.__related__(item):
            return default
        return item

    find = BaseState.find
