from __future__ import annotations

from typing import Any, Dict, Tuple


class HTTPError(Exception):
    def __init__(self, response, data) -> None:
        super().__init__()
        self.response = response
        self.data = data


class HTTPEndpoint:
    def __init__(self, method: str, url: str, *,
                 params: Tuple[str, ...] = (),
                 json: Tuple[str, ...] = ()) -> None:
        self.method = method
        self.url = url
        self.params = params
        self.json = json

    def request(self, *, session,
                fmt: Dict[str, Any] = {}, params=None,
                json=None, **kwargs):
        if params is not None:
            params = {k: v for k, v in params.items() if k in self.params}

        if json is not None:
            json = {k: v for k, v in json.items() if k in self.json}

# TODO: Form params, arrays of json objects


BASE_API_URL = 'https://discord.com/api/v8/'

get_guild_audit_log = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/audit-logs',
    params=('user_id', 'action_type', 'before', 'limit'),
)

get_channel = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'channels/%(channel_id)s',
)

modify_channel = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'channels/%(channel_id)s',
    json=('name', 'type', 'position', 'topic', 'nsfw',
          'ratelimit_per_user', 'bitrrate', 'user_limit',
          'permission_overwrites', 'parent_id'),
)

delete_channel = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'channels/%(channel_id)s',
)

get_channel_messages = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'channels/%(channel_id)s/messages',
    params=('around', 'before', 'after', 'limit'),
)

get_channel_message = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'channels/%(channel_id)s/messages/%(message_id)s',
)

create_channel_message = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'channels/%(channel_id)s/messages',
    json=('content', 'nonce', 'tts', 'embed', 'allowed_mentions',
          'message_reference'),
)

crosspost_message = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'channels/%(channel_id)s/messages/%(message_id)s/crosspost',
)

create_reaction = HTTPEndpoint(
    'PUT',
    BASE_API_URL
    + 'channels/%(channel_id)s/messages/'
    + '%(message_id)s/reactions/%(emoji)s/@me',
)

delete_reaction = HTTPEndpoint(
    'DELETE',
    BASE_API_URL
    + 'channels/%(channel_id)s/messages/'
    + '%(message_id)s/reactions/%(emoji)s/%(user_id)s'
)

get_reactions = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'channels/%(channel_id)s/messages/%(message_id)s/reactions'
)

delete_reactions = HTTPEndpoint(
    'DELETE',
    BASE_API_URL
    + 'channels/%(channel_id)s/messages/%(message_id)s/reactions/%(emoji)s',
    # emoji may be an empty string
)

edit_message = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'channels/%(channel_id)s/messages/%(message_id)s',
    json=('content', 'embed', 'flags', 'allowed_mentions'),
)

delete_message = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'channels/%(channel_id)s/messages/%(message_id)s',
)

bulk_delete_messages = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'channels/%(channel_id)s/messages/bulk-delete',
    json=('messages',),
)

edit_channel_permissions = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'channels/%(channel_id)s/permissions/%(overwrite_id)s',
    json=('allow', 'deny', 'type'),
)

get_channel_invites = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'channels/%(channel_id)s/invites',
)

create_channel_invite = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'channels/%(channel_id)s/invites',
    json=('max_age', 'max_uses', 'temporary', 'unique', 'target_type',
          'target_user_id', 'target_application_id'),
)

delete_channel_permission = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'channels/%(channel_id)s/invites/%(overwrite_id)s',
)

follow_news_channel = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'channels/%(channel_id)s/followers',
    json=('webhook_channel_id',),
)

trigger_typing_indicator = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'channels/%(channel_id)s/typing',
)

get_pinned_messages = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'channels/%(channel_id)s/pins',
)

add_pinned_messages = HTTPEndpoint(
    'PUT',
    BASE_API_URL + 'channels/%(channel_id)s/pins/%(message_id)s',
)

delete_pinned_messages = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'channels/%(channel_id)s/pins/%(message_id)s',
)

add_group_dm_recipient = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'channels/%(channel_id)s/recipients/%(user_id)s',
    json=('access_token', 'nick'),
)

delete_group_dm_recipient = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'channels/%(channel_id)s/recipients/%(user_id)s',
)

get_guild_emojis = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/emojis',
)

get_guild_emoji = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/emojis/%(emoji)s',
)

create_guild_emoji = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'guilds/%(guild_id)s/emojis',
    json=('name', 'image', 'roles'),
)

modify_guild_emoji = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'guilds/%(guild_id)s/emojis/%(emoji)s',
    json=('name', 'roles'),
)

create_guild = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'guilds',
    json=('name', 'region', 'icon', 'verification_level',
          'default_message_notifications', 'explicit_content_filter',
          'roles', 'channels', 'afk_channel_id', 'afk_timeout',
          'system_channel_id', 'system_channel_flags'),
)

get_guild = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s',
    params=('with_counts',),
)

get_guild_preview = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/preview',
)

modify_guild = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'guilds/%(guild_id)s',
    json=('name', 'region', 'icon', 'verification_level',
          'default_message_notifications', 'explicit_content_filter',
          'afk_channel_id', 'afk_timeout', 'owner_id', 'splash',
          'discovery_splash', 'banner', 'system_channel_id',
          'system_channel_flags', 'rules_channel_id',
          'public_updates_channel_id', 'preferred_locals',
          'features', 'description'),
)

delete_guild = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'guilds/%(guild_id)s',
)

get_guild_channels = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/channels',
)

create_guild_channel = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'guilds/%(guild_id)s/channels',
    json=('name', 'type', 'topic', 'bitrate', 'user_limit',
          'ratelimit_per_user', 'position', 'permission_overwrites',
          'parent_id', 'nsfw'),
)

modify_guild_channel_permissions = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'guilds/%(guild_id)s/channels',
    json=('id', 'position', 'lock_permissions', 'parent_id')
)

get_guild_member = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/members/%(user_id)s',
)

get_guild_members = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/members',
    params=('limit', 'after'),
)

search_guild_members = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/members/search',
    params=('query', 'limit'),
)

add_guild_member = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'guilds/%(guild_id)s/members/%(user_id)s',
    json=('access_token', 'nick', 'roles', 'mute', 'deaf'),
)

modify_guild_member = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'guilds/%(guild_id)s/members/%(user_id)s',
    json=('nick', 'roles', 'mute', 'deaf', 'channel_id'),
)

modify_user_client_nick = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'guilds/%(guild_id)s/members/@me/nick',
    json=('nick',),
)

add_guild_member_role = HTTPEndpoint(
    'PUT',
    BASE_API_URL + 'guilds/%(guild_id)s/members/%(user_id)s/roles/%(role_id)s',
)

remove_guild_member_role = HTTPEndpoint(
    'DELTE',
    BASE_API_URL + 'guilds/%(guild_id)s/members/%(user_id)s/roles/%(role_id)s',
)

remove_guild_member = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'guilds/%(guild_id)s/members/%(user_id)s',
)

get_guild_bans = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/bans',
)

get_guild_ban = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/bans/%(user_id)s'
)

create_guild_ban = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'guilds/%(guild_id)s/bans/%(user_id)s',
    json=('delete_message_days', 'reason'),
)

remove_guild_ban = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'guilds/%(guild_id)s/bans/%(user_id)s',
)

get_guild_roles = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/roles',
)

create_guild_role = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'guilds/%(guild_id)s/roles',
    json=('name', 'permissions', 'color', 'hoist', 'mentionable'),
)

modify_guild_role_permissions = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'guilds/%(guild_id)s/roles',
    json=('id', 'position',),
)

modify_guild_role = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'guilds/%(guild_id)s/roles/%(role_id)s',
    json=('name', 'permissions', 'color', 'hoist', 'mentionable'),
)

delete_guild_role = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'guilds/%(guild_id)s/roles/%(role_id)s',
)

get_guild_prune_count = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/prune',
    params=('days', 'include_roles'),
)

begin_guild_prune = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'guilds/%(guild_id)s/prune',
    json=('days', 'compute_prune_count', 'include_roles'),
)

get_guild_voice_regions = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/regions',
)

get_guild_invites = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/invites',
)

get_guild_integrations = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/integrations',
)

get_guild_integration = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/integrations/%(integration_id)s',
)

get_guild_widget_settings = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/widget',
)

modify_guild_widget = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'guilds/%(guild_id)s/widget',
    json=('enabled', 'channel_id')
)

get_guild_widget = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/widget.json',
)

get_guild_vanity_url = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/vanity-url',
)

get_guild_widget_image = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/widget.png',
    params=('style',),
)

get_guild_welcome_screen = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/welcome-screen',
)

modify_guild_welcome_screen = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'guilds/%(guild_id)s/welcome-screen',
    json=('enabled', 'welcome_channels', 'description'),
)

update_current_user_vioce_state = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'guilds/%(guild_id)s/voice-states/@me',
    json=('channel_id', 'suppress', 'request_to_speak_timestamp'),
)

update_user_voice_state = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'guilds/%(guild_id)s/voice-states/%(user_id)s',
    json=('channel_id', 'suppress'),
)

get_invite = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'invites/%(invite_code)s',
)

delete_invite = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'invites/%(invite_code)s',
)

get_template = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/templates/%(template_code)s',
)

create_guild_from_template = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'guilds/templates/%(template_code)s',
    json=('name', 'icon'),
)

get_guild_templates = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'guilds/%(guild_id)s/templates'
)

create_guild_template = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'guilds/%(guild_id)s/templates',
    json=('name', 'description'),
)

sync_guild_template = HTTPEndpoint(
    'PUT',
    BASE_API_URL + 'guilds/%(guild_id)s/templates/%(template_code)s',
)

modify_guild_template = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'guilds/%(guild_id)s/templates/%(template_code)s',
    json=('name', 'description'),
)

delete_guild_template = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'guilds/%(guild_id)s/templates/%(template_code)s',
)

get_user_client = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'users/@me',
)

get_user = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'users/%(user_id)s'
)

modify_user_client = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + 'users/@me',
    json=('username', 'avatar'),
)

get_user_client_guilds = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'users/@me/guilds',
    params=('before', 'after', 'limit'),
)

leave_guild = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'users/@me/guilds/%(guild_id)s',
)

create_dm = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'users/@me/channels',
    json=('recipient_id',),
)

create_group_dm = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'users/@me/channels',
    json=('access_tokens', 'nicks'),
)

get_user_connections = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'users/@me/connections'
)

get_voice_regions = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'voice/regions',
)

create_webhook = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'channels/%(channel_id)s/webhooks',
    json=('name', 'avatar'),
)

get_channel_webhooks = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'channels/%(channel_id)s/webhooks',
)

get_guild_webhooks = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'channels/%(guild_id)s/webhooks',
)

get_webhook = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'webhooks/%(webhook_id)s'
)

get_webhook_with_token = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'webhooks/%(webhook_id)s/%(webhook_token)s',
)

modify_webhook = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'webhooks/%(webhook_id)s',
    json=('name', 'avatar', 'channel_id'),
)

modify_webhook_with_token = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'webhooks/%(webhook_id)s/%(webhook_token)s',
    json=('name', 'avatar'),
)

delete_webhook = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'webhooks/%(webhook_id)s',
)

delete_webhook_with_token = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + 'webhooks/%(webhook_id)s/%(webhook_token)s',
)

execute_webhook = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'webhooks/%(webhook_id)s/%(webhook_token)s',
    params=('wait',),
    json=('content', 'username', 'avatar_url', 'tts', 'file', 'embeds',
          'payload_json', 'allowed_mentions'),
)

execute_slack_webhook = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'webhooks/%(webhook_id)s/%(webhook_token)s',
    params=('wait',),
)

execute_github_webhook = HTTPEndpoint(
    'POST',
    BASE_API_URL + 'webhooks/%(webhook_id)s/%(webhook_token)s',
    params=('wait',),
)

edit_webhook_message = HTTPEndpoint(
    'PATCH',
    BASE_API_URL
    + 'webhooks/%(webhook_id)s/%(webhook_token)s'
    + '/messages/%(message_id)s',
    json=('content', 'embeds', 'file', 'payload_json', 'allowed_mentions'),
)

delete_webhook_message = HTTPEndpoint(
    'DELETE',
    BASE_API_URL
    + 'webhooks/%(webhook_id)s/%(webhook_token)s'
    + '/messages/%(message_id)s',
)

get_gateway = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'gateway'
)

get_gateway_bot = HTTPEndpoint(
    'GET',
    BASE_API_URL + 'gateway/bot'
)


class RestSession:
    def __init__(*args, **kwargs):
        pass


class RestFuture:
    pass
