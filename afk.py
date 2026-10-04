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

    @command("afk", emoji="💤")
    async def afk(self, message):
        """[причина] — включить автоответ"""
        reason = utils.get_args_raw(message).strip()
        self.set("state", {"since": time.time(), "reason": reason})
        self._replied.clear()
        await utils.answer(
            message,
            utils.card(
                "💤 <b>AFK включён</b>",
                f"💬 Причина: {utils.escape_html(reason)}" if reason else None,
                hint="в личке отвечу, что вас нет; выключить — <code>.unafk</code> или просто напишите что-нибудь",
            ),
        )

    @command("unafk", emoji="👋")
    async def unafk(self, message):
        """— выключить автоответ"""
        state = self.get("state")
        if not state:
            await utils.answer(message, "❌ <b>AFK и так выключен</b>")
            return
        self.db.delete("state")
        away = utils.format_duration(time.time() - state["since"])
        await utils.answer(message, f"👋 <b>С возвращением!</b> · вас не было <code>{away}</code>")

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
        text = utils.card(
            f"💤 <b>Меня нет уже</b> <code>{utils.format_duration(now - state['since'])}</code>",
            f"💬 {utils.escape_html(state['reason'])}" if state["reason"] else None,
            hint="отвечу, как только вернусь",
        )
        await message.reply(text, parse_mode="html")
