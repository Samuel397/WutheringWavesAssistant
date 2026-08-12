from __future__ import annotations

import ast
from pathlib import Path
from string import Formatter
from unittest.mock import patch
import xml.etree.ElementTree as ET

from PySide6.QtCore import QLocale, QTranslator
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF

from src.gui.common import resource  # noqa: F401  Registers :/gallery resources.
from src.gui.common.config import BossNameEnum, Language, LanguageSerializer, cfg, paramConfig


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "src" / "gui" / "resource" / "i18n" / "gallery.pt_BR.ts"


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _literal_string(node.left), _literal_string(node.right)
        return left + right if left is not None and right is not None else None
    if isinstance(node, ast.JoinedStr):
        parts = [_literal_string(value) for value in node.values]
        return "".join(parts) if all(part is not None for part in parts) else None
    return None


def _gui_context_sources() -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.classes: list[str] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self.classes.append(node.name)
            self.generic_visit(node)
            self.classes.pop()

        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Attribute):
                context = self.classes[-1] if self.classes else ""
                source = None
                if node.func.attr == "tr" and node.args:
                    source = _literal_string(node.args[0])
                elif node.func.attr == "translate" and len(node.args) >= 2:
                    source = _literal_string(node.args[1])
                    context = _literal_string(node.args[0]) or context
                if context and source is not None:
                    pairs.add((context, source))
            self.generic_visit(node)

    for path in sorted((ROOT / "src" / "gui").rglob("*.py")):
        if path.name == "resource.py":
            continue
        Visitor().visit(ast.parse(path.read_text(encoding="utf-8"), filename=str(path)))
    return pairs


def _catalog() -> tuple[set[tuple[str, str]], list[str]]:
    root = ET.parse(CATALOG).getroot()
    assert root.get("language") == "pt_BR"
    pairs = set()
    unfinished = []
    for context in root.findall("context"):
        context_name = context.findtext("name") or ""
        for message in context.findall("message"):
            source = message.findtext("source") or ""
            translation = message.findtext("translation") or ""
            pairs.add((context_name, source))
            if not translation.strip():
                unfinished.append(f"{context_name}: {source}")
    return pairs, unfinished


def test_pt_br_is_a_serializable_default_ui_language():
    locale = Language.PORTUGUESE_BRAZIL.value
    assert locale.name() == "pt_BR"
    assert cfg.language.defaultValue is Language.PORTUGUESE_BRAZIL
    serializer = LanguageSerializer()
    assert serializer.serialize(Language.PORTUGUESE_BRAZIL) == "pt_BR"
    assert serializer.deserialize("pt_BR") is Language.PORTUGUESE_BRAZIL


def test_pt_br_catalog_covers_every_static_gui_translation():
    catalog_pairs, unfinished = _catalog()
    assert not unfinished
    assert not (_gui_context_sources() - catalog_pairs)


def test_pt_br_catalog_preserves_format_fields():
    formatter = Formatter()
    root = ET.parse(CATALOG).getroot()
    for message in root.findall(".//message"):
        source = message.findtext("source") or ""
        translation = message.findtext("translation") or ""
        source_fields = {field for _, field, _, _ in formatter.parse(source) if field}
        translation_fields = {field for _, field, _, _ in formatter.parse(translation) if field}
        assert translation_fields == source_fields, source


def test_embedded_pt_br_qm_loads_and_translates_wwa_and_fluent_widgets():
    translator = QTranslator()
    assert translator.load(QLocale("pt_BR"), "gallery", ".", ":/gallery/i18n")
    assert translator.translate("SettingInterface", "Settings") == "Configurações"
    assert translator.translate("DailyWidget", "任务设置") == "Configurações de tarefas"
    assert translator.translate("SwitchButton", "Off") == "Desativado"
    assert translator.translate("BossNameOptionsSettingCard", "无妄者") == "Insone"
    assert translator.translate("BossRushWidget", "无妄者") == "Insone"


def test_boss_widgets_render_localized_names_but_keep_enum_ids():
    app = QApplication.instance() or QApplication([])
    translator = QTranslator(app)
    assert translator.load(QLocale("pt_BR"), "gallery", ".", ":/gallery/i18n")
    app.installTranslator(translator)

    from src.gui.view.home.echo import BossRushWidget
    from src.gui.view.param_interface import BossNameOptionsSettingCard

    home_widget = BossRushWidget()
    assert home_widget.checkCards[BossNameEnum.Dreamless].text() == "Insone"
    assert home_widget.checkCards[BossNameEnum.Dreamless].property("boss") is BossNameEnum.Dreamless

    settings_card = BossNameOptionsSettingCard(
        paramConfig.bossName,
        FIF.LABEL,
        "Chefes selecionados",
    )
    dreamless_button = next(
        button
        for button in settings_card.buttonGroup
        if button.property(paramConfig.bossName.name) is BossNameEnum.Dreamless
    )
    assert dreamless_button.text() == "Insone"

    settings_card.deleteLater()
    home_widget.deleteLater()
    app.removeTranslator(translator)


def test_home_renders_localized_device_and_double_reward_tip_but_keeps_device_id():
    app = QApplication.instance() or QApplication([])
    translator = QTranslator(app)
    assert translator.load(QLocale("pt_BR"), "gallery", ".", ":/gallery/i18n")
    app.installTranslator(translator)

    from src.gui.view.home_interface import BasicSettingWidget, BottomWidget, TimeRange

    settings = BasicSettingWidget()
    auto_index = settings.deviceComboBox.findData("Auto")
    assert auto_index >= 0
    assert settings.deviceComboBox.itemText(auto_index) == "Automático"
    assert settings.deviceComboBox.itemData(auto_index) == "Auto"

    with patch.object(TimeRange, "contains", side_effect=[False, True]):
        bottom = BottomWidget()
    assert bottom.tipsLabel.text() == (
        '<b><font color="red">Hoje: recompensas em dobro nos Campos Tacet</font></b>'
    )

    bottom.timer.stop()
    bottom.deleteLater()
    settings.deleteLater()
    app.removeTranslator(translator)
