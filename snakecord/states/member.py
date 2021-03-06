from __future__ import annotations

from typing import TYPE_CHECKING, Type

from .base import BaseState, SnowflakeMapping, WeakValueSnowflakeMapping
from ..objects.member import GuildMember

if TYPE_CHECKING:
    from ..objects.guild import Guild
    from ..manager import BaseManager


class GuildMemberState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __guild_member_class__ = GuildMember

    def __init__(self, *, manager: BaseManager, guild: Guild):
        super().__init__(manager=manager)
        self.guild = guild

    @classmethod
    def set_guild_member_class(cls, klass: Type[GuildMember]) -> None:
        cls.__guild_member_class__ = klass

    def append(self, data: dict, *args, **kwargs) -> GuildMember:
        member = self.get(data['user']['id'])
        if member is not None:
            member._update(data)
        else:
            member = self.__guild_member_class__.unmarshal(
                data, state=self, guild=self.guild, *args, **kwargs)
            member.cache()

        return member
