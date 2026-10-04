# meta developer: @uroboros
# meta version: 1.0
# meta permissions: none
# requires_uroboros: 1.0
"""AFK: пока вас нет, бот отвечает в личке, где вы и как давно."""

import time

from uroboros import ConfigValue, Module, ModuleConfig, command, utils, validators, watcher


class AFK(Module):
    """Автоответ в личке, пока вас нет"""

    def __init__(self):
        self.config = ModuleConfig(
            ConfigValue(
                "cooldown",
                10,
                "Отвечать одному собеседнику не чаще, чем раз в столько минут",
                validators.Integer(minimum=1, maximum=24 * 60),
            ),
            ConfigValue(
                "auto_off",
                True,
                "Выключать AFK, когда вы сами что-то пишете",
                validators.Boolean(),
            ),
        )
        self._replied = {}  # id собеседника → когда отвечали

    @command("afk")
    async def afk(self, message):
        """[причина] — включить автоответ"""
        reason = utils.get_args_raw(message).strip()
        self.set("state", {"since": time.time(), "reason": reason})
        self._replied.clear()
        text = "✅ <b>AFK включён</b>"
        if reason:
            text += "\n" + utils.quote(utils.escape_html(reason))
        await utils.answer(message, text)

    @command("unafk")
    async def unafk(self, message):
        """— выключить автоответ"""
        state = self.get("state")
        if not state:
            await utils.answer(message, "❌ AFK и так выключен")
            return
        self.db.delete("state")
        await utils.answer(
            message, f"✅ AFK выключен · вас не было {utils.format_duration(time.time() - state['since'])}"
        )

    @watcher(only_outgoing=True)
    async def back(self, message):
        """Вы что-то написали сами — значит, вернулись."""
        if not self.config["auto_off"] or not self.get("state"):
            return
        if (message.raw_text or "").startswith(utils.get_prefix(self.db.raw)):
            return  # команды, в том числе сама .afk, не считаются
        self.db.delete("state")

    @watcher(only_incoming=True, filter=lambda m: m.is_private)
    async def reply(self, message):
        state = self.get("state")
        if not state:
            return
        sender = await message.get_sender()
        if sender is None or getattr(sender, "bot", False):
            return
        now = time.time()
        if now - self._replied.get(sender.id, 0) < self.config["cooldown"] * 60:
            return
        self._replied[sender.id] = now
        text = f"💤 Меня нет уже {utils.format_duration(now - state['since'])}"
        if state["reason"]:
            text += "\n" + utils.quote(utils.escape_html(state["reason"]))
        await message.reply(text, parse_mode="html")
