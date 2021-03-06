from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseObject
from ..templates.user import UserTemplate

if TYPE_CHECKING:
    from ..states.user import UserState


class User(BaseObject, template=UserTemplate):
    __slots__ = ()

    def __init__(self, *, state: UserState):
        super().__init__(state=state)

    @property
    def mention(self):
        return f'<@{self.id}>'
