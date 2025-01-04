#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime
from typing import Optional

import pyrogram
from pyrogram import raw, types, utils
from ..messages_and_media import Str
from ..object import Object


class UserGift(Object):
    """Represents a gift received by a user.

    Parameters:
        sender_user (:obj:`~pyrogram.types.User`, *optional*):
            Identifier of the user that sent the gift; None if unknown.

        text (``str``, *optional*):
            Message added to the gift.
        
        entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            For text messages, special entities like usernames, URLs, bot commands, etc. that appear in the text.

        is_private (``bool``, *optional*):
            True, if the sender and gift text are shown only to the gift receiver; otherwise, everyone are able to see them.

        is_saved (``bool``, *optional*):
            True, if the gift is displayed on the user's profile page; may be False only for the receiver of the gift.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the gift was sent.

        gift (:obj:`~pyrogram.types.Gift`, *optional*):
            Information about the gift.
        
        message_id (``int``, *optional*):
            Identifier of the message with the gift in the chat with the sender of the gift; can be None or an identifier of a deleted message; only for the gift receiver.

        sell_star_count (``int``, *optional*):
            Number of Telegram Stars that can be claimed by the receiver instead of the gift; only for the gift receiver.

        was_converted (``bool``, *optional*):
            True, if the gift was converted to Telegram Stars; only for the receiver of the gift.

        can_be_upgraded (``bool``, *optional*):
            True, if the gift is a regular gift that can be upgraded to a unique gift; only for the receiver of the gift.

        was_refunded (``bool``, *optional*):
            True, if the gift was refunded and isn't available anymore.

        prepaid_upgrade_star_count (``int``, *optional*):
            Number of Telegram Stars that were paid by the sender for the ability to upgrade the gift.

        can_be_transferred (``bool``, *optional*):
            True, if the gift is an upgraded gift that can be transferred to another user; only for the receiver of the gift.

        transfer_star_count (``int``, *optional*):
            Number of Telegram Stars that must be paid to transfer the upgraded gift; only for the receiver of the gift.

        export_date (:py:obj:`~datetime.datetime`, *optional*):
            Point in time (Unix timestamp) when the upgraded gift can be transferred to TON blockchain as an NFT; None if NFT export isn't possible; only for the receiver of the gift.

    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        sender_user: Optional["types.User"] = None,
        text: Optional[str] = None,
        entities: list["types.MessageEntity"] = None,
        date: datetime,
        is_private: Optional[bool] = None,
        is_saved: Optional[bool] = None,
        gift: Optional["types.Gift"] = None,
        message_id: Optional[int] = None,
        sell_star_count: Optional[int] = None,
        was_converted: Optional[bool] = None,
        can_be_upgraded: Optional[bool] = None,
        was_refunded: Optional[bool] = None,
        prepaid_upgrade_star_count: Optional[int] = None,
        can_be_transferred: Optional[bool] = None,
        transfer_star_count: Optional[int] = None,
        export_date: datetime = None,
    ):
        super().__init__(client)

        self.date = date
        self.gift = gift
        self.is_private = is_private
        self.is_saved = is_saved
        self.sender_user = sender_user
        self.text = text
        self.entities = entities
        self.message_id = message_id
        self.sell_star_count = sell_star_count
        self.was_converted = was_converted
        self.can_be_upgraded = can_be_upgraded
        self.was_refunded = was_refunded
        self.prepaid_upgrade_star_count = prepaid_upgrade_star_count
        self.can_be_transferred = can_be_transferred
        self.transfer_star_count = transfer_star_count
        self.export_date = export_date


    @staticmethod
    async def _parse(
        client,
        user_star_gift: "raw.types.UserStarGift",
        users: dict
    ) -> "UserGift":
        text, entities = None, None
        if getattr(user_star_gift, "message", None):
            text = user_star_gift.message.text or None
            entities = [types.MessageEntity._parse(client, entity, users) for entity in user_star_gift.message.entities]
            entities = types.List(filter(lambda x: x is not None, entities))

        return UserGift(
            date=utils.timestamp_to_datetime(user_star_gift.date),
            gift=await types.Gift._parse(client, user_star_gift.gift),
            is_private=getattr(user_star_gift, "name_hidden", None),
            is_saved=not user_star_gift.unsaved if getattr(user_star_gift, "unsaved", None) else None,
            sender_user=types.User._parse(client, users.get(user_star_gift.from_id)) if getattr(user_star_gift, "from_id", None) else None,
            message_id=getattr(user_star_gift, "msg_id", None),
            sell_star_count=getattr(user_star_gift, "convert_stars", None),
            text=Str(text).init(entities) if text else None,
            entities=entities,
            client=client
        )

    @staticmethod
    async def _parse_action(
        client,
        message: "raw.base.Message",
        users: dict
    ) -> "UserGift":
        action = message.action

        doc = action.gift.sticker
        attributes = {type(i): i for i in doc.attributes}

        text, entities = None, None
        if getattr(action, "message", None):
            text = action.message.text or None
            entities = [types.MessageEntity._parse(client, entity, users) for entity in action.message.entities]
            entities = types.List(filter(lambda x: x is not None, entities))

        if isinstance(action, raw.types.MessageActionStarGift):
            return UserGift(
                gift=types.Gift(
                    id=action.gift.id,
                    sticker=await types.Sticker._parse(client, doc, attributes),
                    star_count=action.gift.stars,
                    total_count=getattr(action.gift, "availability_total", None),
                    remaining_count=getattr(action.gift, "availability_remains", None),
                    default_sell_star_count=action.gift.convert_stars,
                    is_limited=getattr(action.gift, "limited", None),
                ),
                date=utils.timestamp_to_datetime(message.date),
                is_private=getattr(action, "name_hidden", None),
                is_saved=getattr(action, "saved", None),
                sender_user=types.User._parse(client, users.get(utils.get_raw_peer_id(message.peer_id))),
                message_id=message.id,
                text=Str(text).init(entities) if text else None,
                entities=entities,
                sell_star_count=getattr(action, "convert_stars", None),
                was_converted=getattr(action, "converted", None),
                can_be_upgraded=getattr(action, "can_upgrade", None),
                was_refunded=getattr(action, "refunded", None),
                prepaid_upgrade_star_count=getattr(action, "upgrade_stars", None),
                client=client
            )

        if isinstance(action, raw.types.MessageActionStarGiftUnique):
            return UserGift(
                gift=types.Gift(
                    id=action.gift.id,
                    sticker=await types.Sticker._parse(client, doc, attributes),
                    star_count=action.gift.stars,
                    total_count=getattr(action.gift, "availability_total", None),
                    remaining_count=getattr(action.gift, "availability_remains", None),
                    default_sell_star_count=action.gift.convert_stars,
                    is_limited=getattr(action.gift, "limited", None),
                ),
                date=utils.timestamp_to_datetime(message.date),
                sender_user=types.User._parse(client, users.get(utils.get_raw_peer_id(message.peer_id))),
                message_id=message.id,
                text=Str(text).init(entities) if text else None,
                entities=entities,
                can_be_transferred=getattr(action, "transferred", None),
                was_refunded=getattr(action, "refunded", None),
                prepaid_upgrade_star_count=getattr(action, "upgrade_stars", None),
                export_date=utils.timestamp_to_datetime(action.can_export_at) if action.can_export_at else None,
                transfer_star_count=getattr(action, "transfer_stars", None),
                client=client
            )

    async def toggle(self, is_saved: bool) -> bool:
        """Bound method *toggle* of :obj:`~pyrogram.types.UserGift`.

        Use as a shortcut for:

        .. code-block:: python

            await client.toggle_gift_is_saved(
                sender_user_id=user_id,
                message_id=message_id
            )

        Parameters:
            is_saved (``bool``):
                Pass True to display the gift on the user's profile page; pass False to remove it from the profile page.

        Example:
            .. code-block:: python

                await user_gift.toggle(is_saved=False)

        Returns:
            ``bool``: On success, True is returned.

        """
        return await self._client.toggle_gift_is_saved(
            sender_user_id=self.sender_user.id,
            message_id=self.message_id,
            is_saved=is_saved
        )
