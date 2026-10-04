# meta developer: @uroboros
# meta version: 1.0
# meta permissions: network
# requires_uroboros: 1.0
"""Погода сейчас с wttr.in."""

import urllib.parse

import aiohttp
from uroboros import ConfigValue, Module, ModuleConfig, command, utils, validators

URL = "https://wttr.in/{city}?format=4&lang=ru"


class Weather(Module):
    """Погода с wttr.in"""

    def __init__(self):
        self.config = ModuleConfig(
            ConfigValue("city", "", "Город по умолчанию", validators.String(max_len=100)),
        )

    @command("weather", access="support", emoji="🌤")
    async def weather(self, message):
        """[город] — погода сейчас; город по умолчанию — .cfg weather city"""
        city = utils.get_args_raw(message).strip() or self.config["city"]
        if not city:
            await utils.answer(
                message,
                utils.card(
                    "❌ <b>Какой город?</b>",
                    hint="<code>.weather Москва</code> или город по умолчанию: <code>.cfg weather city</code>",
                ),
            )
            return
        await utils.answer(message, "⏳ <b>Узнаю погоду...</b>")
        url = URL.format(city=urllib.parse.quote(city))
        try:
            # wttr.in отдаёт короткий текст, если считает клиента консольным.
            async with (
                aiohttp.ClientSession(headers={"User-Agent": "curl/8"}) as session,
                session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response,
            ):
                text = (await response.text()).strip()
                ok = response.status == 200
        except (aiohttp.ClientError, TimeoutError) as e:
            await utils.answer(message, utils.card("❌ <b>wttr.in не ответил</b>", utils.escape_html(e)))
            return
        if not ok or not text or "Unknown location" in text:
            await utils.answer(message, f"❌ <b>Не нашёл погоду для {utils.escape_html(city)}</b>")
            return
        await utils.answer(message, f"🌤 <b>{utils.escape_html(city)}</b>\n" + utils.quote(utils.escape_html(text)))
