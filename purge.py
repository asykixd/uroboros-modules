# meta developer: @uroboros
# meta version: 1.0
# meta permissions: none
# requires_uroboros: 1.0
"""Удаление своих сообщений: одного или всех от выбранного до команды."""

from uroboros import Module, command, utils

CHUNK = 100  # столько сообщений Telegram удаляет одним запросом


class Purge(Module):
    """Удаление своих сообщений"""

    @command("purge", access="owner", emoji="🧹")
    async def purge(self, message):
        """(ответом) — удалить свои сообщения от того, на которое ответили, до команды"""
        reply = await utils.get_reply(message)
        if reply is None:
            await utils.answer(message, "❌ <b>Ответьте на сообщение, с которого начать</b>")
            return
        ids = [
            msg.id
            async for msg in self.client.iter_messages(message.chat_id, min_id=reply.id - 1, from_user="me")
            if msg.id <= message.id
        ]
        for start in range(0, len(ids), CHUNK):
            await self.client.delete_messages(message.chat_id, ids[start : start + CHUNK])

    @command("del", access="owner", emoji="🗑")
    async def delete(self, message):
        """(ответом) — удалить сообщение, на которое ответили, и команду"""
        reply = await utils.get_reply(message)
        if reply is None:
            await utils.answer(message, "❌ <b>Ответьте на сообщение, которое удалить</b>")
            return
        await self.client.delete_messages(message.chat_id, [reply.id, message.id])
