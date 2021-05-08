from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Type, Union

from ...connections.shard import Shard
from ...manager import BaseManager
from ...utils.events import EventNamespace, EventDefinition

if TYPE_CHECKING:
    from ...objects.channel import Channel, TextChannel
    from ...objects.emoji import GuildEmoji
    from ...objects.guild import Guild
    from ...objects.member import GuildMember
    from ...objects.message import Message
    from ...objects.role import Role
    from ...objects.user import User


@dataclass
class _base_event(EventDefinition):
    manager: UserClientManager
    shard: Shard
    payload: Dict[str, Any]


class UserClientEvents(EventNamespace):
    @dataclass
    class application_command_create(_base_event):
        pass

    @dataclass
    class application_command_update(_base_event):
        pass

    @dataclass
    class application_command_delete(_base_event):
        pass

    @dataclass
    class channel_create(_base_event):
        channel: Optional[Channel] = None

        def __post_init__(self):
            guild = self.manager.guilds.get(self.payload.get('guild_id'))
            if guild is not None:
                self.channel = self.manager.channels.append(
                    self.payload, guild=guild)

    @dataclass
    class channel_update(_base_event):
        channel: Optional[Channel] = None

        def __post_init__(self):
            guild = self.manager.guilds.get(self.payload.get('guild_id'))

            if guild is None:
                self.channel = self.manager.channels.append(
                    self.payload)
            else:
                self.channel = self.manager.channels.append(
                    self.payload, guild=guild)

    @dataclass
    class channel_delete(_base_event):
        channel: Optional[Union[Channel, int]] = None

        def __post_init__(self):
            channel_id = self.payload.get('id')
            self.channel = self.manager.channels.pop(channel_id, channel_id)

    @dataclass
    class channel_pins_update(_base_event):
        pass

    @dataclass
    class guild_create(_base_event):
        guild: Optional[Guild] = None

        def __post_init__(self):
            self.guild = self.manager.guilds.append(self.payload)

    @dataclass
    class guild_update(_base_event):
        guild: Optional[Guild] = None

        def __post_init__(self):
            self.guild = self.manager.guilds.append(self.payload)

    @dataclass
    class guild_delete(_base_event):
        guild: Optional[Guild] = None

        def __post_init__(self):
            guild_id = self.payload.get('guild_id')
            self.guild = self.manager.guilds.pop(guild_id)

    @dataclass
    class guild_ban_add(_base_event):
        guild: Optional[Guild] = None
        user: Optional[User] = None
        member: Optional[GuildMember] = None

        def __post_init__(self):
            guild_id = self.payload.get('guild_id')
            user = self.payload.get('user')
            self.guild = self.manager.get(guild_id)
            self.user = self.manager.users.append(user)
            self.member = self.guild.members.pop(self.user.id, None)

    @dataclass
    class guild_ban_remove(_base_event):
        guild: Optional[Guild] = None
        user: Optional[User] = None

        def __post_init__(self):
            guild_id = self.payload.get('guild')
            user = self.payload.get('user')
            self.guild = self.manager.guilds.get(guild_id)
            self.user = self.manager.users.append(user)

    @dataclass
    class guild_emojis_update(_base_event):
        guild: Optional[Guild] = None
        emojis: Optional[List[GuildEmoji]] = None

        def __post_init__(self):
            guild_id = self.payload.get('guild_id')
            emojis = self.payload.get('emojis')
            self.guild = self.manager.guilds.get(guild_id)
            self.emojis = self.guild.emojis.extend(emojis)

    @dataclass
    class guild_integrations_update(_base_event):
        pass

    @dataclass
    class guild_member_add(_base_event):
        guild: Optional[Guild] = None
        member: Optional[GuildMember] = None

        def __post_init__(self):
            guild_id = self.payload.get('guild_id')
            self.guild = self.manager.guilds.get(guild_id)

            if self.guild is not None:
                self.member = self.guild.members.append(self.payload)

    @dataclass
    class guild_member_remove(_base_event):
        guild: Optional[Guild] = None
        user: Optional[User] = None
        member: Optional[GuildMember] = None

        def __post_init__(self):
            guild_id = self.payload.get('guild_id')
            user = self.payload.get('user')
            self.user = self.manager.users.append(user)
            self.guild = self.manager.guilds.get(guild_id)

            if self.guild is not None:
                self.member = self.guild.members.pop(self.user.id, None)

    @dataclass
    class guild_member_update(_base_event):
        guild: Optional[Guild] = None
        member: Optional[GuildMember] = None

        def __post_init__(self):
            guild_id = self.payload.get('guild_id')
            self.guild = self.manager.guilds.get(guild_id)

            if self.guild is not None:
                self.member = self.guild.members.append(self.payload)

    @dataclass
    class guild_members_chunk(_base_event):
        guild: Optional[Guild] = None
        members: Optional[List[GuildMember]] = None

        def __post_init__(self):
            guild_id = self.payload.get('guild_id')
            members = self.payload.get('members')

            self.guild = self.manager.guilds.get(guild_id)

            if self.guild is not None:
                self.members = self.guild.members.extend(members)

    @dataclass
    class guild_role_create(_base_event):
        guild: Optional[Guild] = None
        role: Optional[Role] = None

        def __post_init__(self):
            guild_id = self.payload.get('guild_id')
            role = self.payload.get('role')

            self.guild = self.manager.guilds.get(guild_id)

            if self.guild is not None:
                self.role = self.guild.roles.append(role)

    @dataclass
    class guild_role_update(_base_event):
        guild: Optional[Guild] = None
        role: Optional[Role] = None

        def __post_init__(self):
            guild_id = self.payload.get('guild_id')
            role = self.payload.get('role')

            self.guild = self.manager.guilds.get(guild_id)

            if self.guild is not None:
                self.role = self.guild.roles.append(role)

    @dataclass
    class guild_role_delete(_base_event):
        guild: Optional[Guild] = None
        role: Optional[Role] = None

        def __post_init__(self):
            guild_id = self.payload.get('guild_id')
            role_id = self.payload.get('role_id')

            self.guild = self.manager.guilds.get(guild_id)

            if self.guild is not None:
                self.role = self.guild.roles.pop(role_id, None)

    @dataclass
    class integration_create(_base_event):
        pass

    @dataclass
    class integration_update(_base_event):
        pass

    @dataclass
    class integration_delete(_base_event):
        pass

    @dataclass
    class interaction_create(_base_event):
        pass

    @dataclass
    class invite_create(_base_event):
        pass

    @dataclass
    class invite_delete(_base_event):
        pass

    @dataclass
    class message_create(_base_event):
        channel: Optional[TextChannel] = None
        message: Optional[Message] = None

        def __post_init__(self):
            channel_id = self.payload.get('channel_id')
            self.channel = self.manager.channels.get(channel_id)

            if self.channel is not None:
                self.message = self.channel.messages.append(self.payload)

    @dataclass
    class message_update(_base_event):
        channel: Optional[Channel] = None
        message: Optional[Message] = None

        def __post_init__(self):
            channel_id = self.payload.get('channel_id')
            self.channel = self.manager.channels.get(channel_id)

            if self.channel is not None:
                self.message = self.channel.messages.append(self.payload)

    @dataclass
    class message_delete(_base_event):
        channel: Optional[Channel] = None
        message: Optional[Message] = None

        def __post_init__(self):
            channel_id = self.payload.get('channel_id')
            message_id = self.payload.get('message_id')
            self.channel = self.manager.channels.get(channel_id)

            if self.channel is not None:
                self.message = self.channel.messages.pop(message_id, None)

    @dataclass
    class message_delete_bulk(_base_event):
        channel: Optional[Channel] = None
        messages: Optional[List[Union[Message, int]]] = None

        def __post_init__(self):
            channel_id = self.payload.get('channel_id')
            message_ids = self.payload.get('message_id')
            self.channel = self.manager.channels.get(channel_id)

            self.messages = []

            if self.channel is not None:
                for message_id in message_ids:
                    self.messages.append(
                        self.channel.messages.pop(message_id, message_id))

    @dataclass
    class message_reaction_add(_base_event):
        pass

    @dataclass
    class message_reaction_remove(_base_event):
        pass

    @dataclass
    class message_reaction_remove_all(_base_event):
        pass

    @dataclass
    class message_reaction_remove_emoji(_base_event):
        pass

    @dataclass
    class presence_update(_base_event):
        pass

    @dataclass
    class typing_state(_base_event):
        pass

    @dataclass
    class user_update(_base_event):
        pass

    @dataclass
    class voice_state_update(_base_event):
        pass

    @dataclass
    class voice_server_update(_base_event):
        pass

    @dataclass
    class webhooks_update(_base_event):
        pass


class UserClientManager(BaseManager):
    events: Type[UserClientEvents] = UserClientEvents

    def __init__(self, token, *args, intents: int, **kwargs) -> None:
        self.shard_range = kwargs.pop('shard_range', range(1))
        self.intents = intents
        self.shards: Dict[int, Shard] = {}
        self.token = token
        super().__init__(*args, **kwargs)

    async def start(self, *args, **kwargs):
        for i in self.shard_range:
            self.shards[i] = await self.create_connection(
                Shard, *args, **kwargs)
