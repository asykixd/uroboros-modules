# Модули Uroboros

Официальные модули для [Uroboros](https://github.com/asykixd/uroboros) — модульного юзербота для Telegram.
Репозиторий подключён в Uroboros по умолчанию, поэтому модули ставятся по имени:

```
.dlm afk
```

Если вы отключали репозиторий: `.addrepo asykixd/uroboros-modules`. Список модулей — `.dlm asykixd/uroboros-modules`.

| Модуль | Команды | Что делает |
|---|---|---|
| [afk](afk.py) | `.afk [причина]`, `.unafk` | автоответ в личке, пока вас нет; выключается, когда вы пишете сами |
| [notes](notes.py) | `.save`, `.note`, `.notes`, `.delnote` | заметки: текст под именем, который можно достать в любом чате |
| [purge](purge.py) | `.purge`, `.del` | удаление своих сообщений: одного или всех от выбранного |
| [weather](weather.py) | `.weather [город]` | погода сейчас с wttr.in |

## Свой репозиторий модулей

Этот репозиторий — шаблон: нажмите **Use this template**, и у вас будет такой же со всеми проверками.

1. Каждый модуль — один `.py`-файл в корне. Имя файла — имя для `.dlm`.
2. В шапке файла:

   ```python
   # meta developer: @вы
   # meta version: 1.0
   # meta permissions: network      # что нужно модулю: network, files, env, processes, exec или none
   # requires_uroboros: 1.0
   ```

3. Пишите на публичном API Uroboros — [документация для авторов модулей](https://asykixd.github.io/uroboros/modules/).
   Отвечайте карточками `utils.card(...)` и давайте командам иконку `@command(emoji=...)` — так модули выглядят
   так же, как встроенные.
4. `tests/test_modules.py` проверяет, что каждый модуль загружается, не конфликтует с остальными и проходит
   проверку кода Uroboros без замечаний: без опасного кода и с объявленными правами. Свои тесты кладите рядом.

Проверить локально:

```bash
python3 -m venv .venv
.venv/bin/pip install "uroboros-userbot @ git+https://github.com/asykixd/uroboros@dev" pytest ruff
.venv/bin/ruff check . && .venv/bin/pytest -q
```

Пользователи подключают ваш репозиторий командой `.addrepo вы/репозиторий` и ставят модули по имени.
Модули из подключённых репозиториев ставятся без лишнего подтверждения, но опасный код всё равно требует
явного согласия.

## Лицензия

AGPL-3.0, как и Uroboros.
