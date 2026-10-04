"""Каждый модуль загружается в Uroboros, проходит проверку кода без замечаний и не конфликтует с остальными."""

import asyncio
from pathlib import Path

import pytest
from uroboros import scan
from uroboros.database import Database
from uroboros.loader import Loader

ROOT = Path(__file__).resolve().parent.parent
MODULES = sorted(path for path in ROOT.glob("*.py") if not path.name.startswith("_"))


class FakeMessage:
    """Своё исходящее сообщение: utils.answer его редактирует."""

    out = True
    is_reply = False

    def __init__(self, text=""):
        self.raw_text = text
        self.edits = []

    async def edit(self, text, **kwargs):
        self.edits.append(text)
        return self


@pytest.fixture
def loader(tmp_path):
    db = Database(":memory:")
    loader = Loader(None, db, tmp_path / "modules")
    asyncio.run(loader.load_all())  # встроенные модули: их команды тоже не должны пересекаться
    yield loader
    asyncio.run(loader.unload_all())
    db.close()


@pytest.mark.parametrize("path", MODULES, ids=lambda p: p.stem)
def test_module_is_clean(path):
    source = path.read_text("utf-8")
    report = scan.scan(source)
    assert report.findings == [], scan.describe(report.findings)
    assert report.declared is not None, "объявите права: # meta permissions: ... (или none)"
    assert "# meta developer:" in source and "# requires_uroboros:" in source


def test_all_modules_load_together(loader):
    for path in MODULES:
        instances = asyncio.run(loader.install(path.read_text("utf-8"), f"file:{path.name}"))
        assert instances and all(loader.module_commands(inst) for inst in instances), path.name
        for inst in instances:
            missing = [cmd.name for cmd in loader.module_commands(inst) if not cmd.info.emoji]
            assert not missing, f"{path.name}: у команд нет иконки @command(emoji=...): {missing}"


def run(loader, text):
    message = FakeMessage(text)
    asyncio.run(loader.get_command(text.split()[0][1:]).func(message))
    return message.edits[-1]


def test_notes(loader):
    asyncio.run(loader.install((ROOT / "notes.py").read_text("utf-8"), "file:notes.py"))
    assert run(loader, ".notes").startswith("🗂 <b>Заметок нет</b>")
    assert "сохранена" in run(loader, ".save Wifi пароль <123>")
    assert "обновлена" in run(loader, ".save wifi пароль 456")
    assert run(loader, ".note WIFI") == "пароль 456"
    assert "note wifi" in run(loader, ".notes")
    assert "удалена" in run(loader, ".delnote wifi")
    assert run(loader, ".note wifi").startswith("❌")


def test_afk(loader):
    asyncio.run(loader.install((ROOT / "afk.py").read_text("utf-8"), "file:afk.py"))
    assert run(loader, ".unafk").startswith("❌")
    assert "сплю" in run(loader, ".afk сплю")
    afk = loader.get_module("afk")
    assert afk.get("state")["reason"] == "сплю"

    # Своё сообщение без префикса — вернулись, AFK выключается.
    asyncio.run(afk.back(FakeMessage("привет")))
    assert afk.get("state") is None
