from __future__ import annotations

import enum
from typing import Dict, TYPE_CHECKING, Type, Union

from .base import (
    BaseState,
    BaseSubState,
    SnowflakeMapping,
    WeakValueSnowflakeMapping,
)
from ..connections import rest
from ..utils.snowflake import Snowflake
from ..objects import channel as channels

if TYPE_CHECKING:
    from ..objects.guild import Guild


class ChannelType(enum.IntEnum):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6


class ChannelState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __default_class__ = channels.GuildChannel
    __class_map__: Dict[ChannelType, Type[channels.Channel]] = {
        ChannelType.GUILD_TEXT: channels.TextChannel,
        ChannelType.GUILD_NEWS: channels.TextChannel,
        ChannelType.GUILD_VOICE: channels.VoiceChannel,
        ChannelType.DM: channels.DMChannel,
        ChannelType.GUILD_CATEGORY: channels.CategoryChannel
    }

    @classmethod
    def set_text_channel_class(cls, klass):
        cls.__class_map__[ChannelType.GUILD_TEXT] = klass

    @classmethod
    def set_voice_channel_class(cls, klass):
        cls.__class_map__[ChannelType.GUILD_VOICE] = klass

    @classmethod
    def set_dm_channel_class(cls, klass):
        cls.__class_map__[ChannelType.DM] = klass

    @classmethod
    def set_category_channel_class(cls, klass):
        cls.__class_map__[ChannelType.GUILD_CATEGORY] = klass

    @classmethod
    def set_default_class(cls, klass):
        cls.__default_class__ = klass

    def append(self, data: dict, *args, **kwargs):
        channel = self.get(data['id'])
        if channel is not None:
            channel._update(data)
        else:
            Class = self.__class_map__.get(data['type'],
                                           self.__default_class__)
            channel = Class.unmarshal(data, state=self, *args, **kwargs)
            channel.cache()

        return channel

    async def fetch(self, channel_id):
        channel_id = Snowflake.try_snowflake(channel_id)
        data = await rest.get_channel.request(
            session=self.manager.rest, fmt={'channel_id': channel_id})
        return self.append(data)


class GuildChannelState(BaseSubState):
    superstate: ChannelState

    def __init__(self, *, superstate: ChannelState, guild: Guild):
        super().__init__(superstate=superstate)
        self.guild = guild

    def __related__(self, item):
        return (isinstance(item, channels.GuildChannel)
                and item.guild == self.guild)
