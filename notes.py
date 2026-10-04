# meta developer: @uroboros
# meta version: 1.0
# meta permissions: none
# requires_uroboros: 1.0
"""Заметки: сохранить текст под именем и быстро достать в любом чате."""

from uroboros import Module, command, utils

MAX_NAME = 64


class Notes(Module):
    """Заметки: текст под именем"""

    def _notes(self):
        return self.get("notes", {})

    @command("save", emoji="💾")
    async def save(self, message):
        """<имя> [текст] — сохранить заметку; без текста — текст сообщения, на которое ответили"""
        args = utils.get_args_raw(message).split(maxsplit=1)
        if not args:
            await utils.answer(
                message, utils.card("❌ <b>Как назвать заметку?</b>", hint="<code>.save имя текст</code>")
            )
            return
        name = args[0].lower()
        if len(name) > MAX_NAME:
            await utils.answer(message, f"❌ <b>Имя длиннее {MAX_NAME} символов</b>")
            return
        text = args[1] if len(args) > 1 else ""
        if not text:
            reply = await utils.get_reply(message)
            text = (reply.raw_text or "") if reply else ""
        if not text:
            await utils.answer(
                message, utils.card("❌ <b>Нет текста</b>", hint="напишите его после имени или ответьте на сообщение")
            )
            return
        notes = self._notes()
        replaced = name in notes
        notes[name] = text
        self.set("notes", notes)
        escaped = utils.escape_html(name)
        await utils.answer(
            message,
            utils.card(
                f"✅ <b>Заметка {'обновлена' if replaced else 'сохранена'}</b>",
                [f"🏷 Имя: <code>{escaped}</code>", f"📏 Длина: <code>{len(text)}</code> символов"],
                hint=f"показать: <code>.note {escaped}</code>",
            ),
        )

    @command("note", emoji="📖")
    async def note(self, message):
        """<имя> — показать заметку"""
        name = utils.get_args_raw(message).strip().lower()
        text = self._notes().get(name)
        if text is None:
            await utils.answer(message, f"❌ <b>Заметки</b> <code>{utils.escape_html(name)}</code> <b>нет</b>")
            return
        await utils.answer(message, utils.escape_html(text))

    @command("notes", emoji="🗂")
    async def notes(self, message):
        """— список заметок"""
        notes = self._notes()
        if not notes:
            await utils.answer(
                message, utils.card("🗂 <b>Заметок нет</b>", hint="сохранить: <code>.save имя текст</code>")
            )
            return
        prefix = utils.escape_html(utils.get_prefix(self.db.raw))
        lines = [f"▸ <code>{prefix}note {utils.escape_html(name)}</code>" for name in sorted(notes)]
        await utils.answer(message, utils.card(f"🗂 <b>Заметки</b> · {len(notes)}", lines, expandable=len(lines) > 10))

    @command("delnote", emoji="🗑")
    async def delnote(self, message):
        """<имя> — удалить заметку"""
        name = utils.get_args_raw(message).strip().lower()
        notes = self._notes()
        if notes.pop(name, None) is None:
            await utils.answer(message, f"❌ <b>Заметки</b> <code>{utils.escape_html(name)}</code> <b>нет</b>")
            return
        self.set("notes", notes)
        await utils.answer(message, f"🗑 <b>Заметка</b> <code>{utils.escape_html(name)}</code> <b>удалена</b>")
