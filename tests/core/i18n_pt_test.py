import ast
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.config.gui_config import ParamConfig
from src.controller.main_controller import configured_game_language
from src.core.i18n import (
    I18N_PAGES,
    I18N_PAGES_BOSS,
    I18N_PAGES_ECHO_MERGE,
    I18N_PAGES_GUIDEBOOK,
    I18N_TEXT,
    I18nPage,
    I18nPageEchoMerge,
    I18nText,
    I18nTr,
    Language,
    PT_I18N_UNRESOLVED,
)
from src.core.pt_i18n import PT_OFFICIAL_TEXT, pt_regex
from src.core.runtime import Device
from src.core.workflow import TaskSpec
from src.service.ocr_service import PaddleOcrServiceImpl, RapidOcrServiceImpl
from src.service.window_service import HwndServiceImpl
from src.util import rapidocr_util


REPO_ROOT = Path(__file__).resolve().parents[2]
EXECUTABLE_WORKFLOWS = (
    "common_workflow.py",
    "daily_workflow.py",
    "boss_workflow.py",
    "explore_workflow.py",
)


def _i18n_keys_in(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "I18nText"
    }


def test_portuguese_inventory_is_complete_or_explicitly_audited():
    assert len(I18N_TEXT) == 378
    assert len(PT_OFFICIAL_TEXT) == 375
    assert PT_I18N_UNRESOLVED == {
        I18nText.Suoming: "not present in the official PT TextMap",
        I18nText.Jingran: "not present in the official PT TextMap",
        I18nText.Hsin: "not present in the official PT TextMap",
    }
    assert set(I18N_TEXT) == set(PT_OFFICIAL_TEXT) | set(PT_I18N_UNRESOLVED)
    assert all(
        Language.PT in translations
        for key, translations in I18N_TEXT.items()
        if key not in PT_I18N_UNRESOLVED
    )
    assert all(
        Language.PT not in I18N_TEXT[key]
        for key in PT_I18N_UNRESOLVED
    )


def test_unreleased_portuguese_names_have_an_explicit_runtime_fallback():
    for key in PT_I18N_UNRESOLVED:
        translated = I18nTr(Language.PT)(key)
        assert translated is I18N_TEXT[key][Language.EN]
        assert translated.raw
        re.compile(translated, re.IGNORECASE)


@pytest.mark.parametrize("filename", EXECUTABLE_WORKFLOWS)
def test_enabled_workflow_i18n_keys_resolve_in_portuguese(filename):
    path = REPO_ROOT / "src" / "service" / filename
    keys = _i18n_keys_in(path)
    assert keys, f"coverage input unexpectedly contains no I18nText keys: {path}"
    unknown = keys - set(I18N_TEXT)
    assert not unknown
    missing = {key for key in keys if Language.PT not in I18N_TEXT[key]}
    assert not missing


@pytest.mark.parametrize(
    "pages",
    (I18N_PAGES, I18N_PAGES_ECHO_MERGE, I18N_PAGES_GUIDEBOOK, I18N_PAGES_BOSS),
)
def test_every_executable_page_has_a_portuguese_definition(pages):
    assert pages
    assert all(Language.PT in translations for translations in pages.values())


def test_handwritten_page_patterns_also_tolerate_accent_loss():
    page = I18N_PAGES[I18nPage.Boss_Dreamless_Enter.PAGE][Language.PT]
    assert re.search(page[I18nPage.Include][I18nPage.Boss_Dreamless_Enter.Dreamless], "Estatua do Destronado")
    page = I18N_PAGES_ECHO_MERGE[I18nPageEchoMerge.DataBank.PAGE][Language.PT]
    assert re.search(
        page[I18nPage.Include][I18nPageEchoMerge.DataBank.DataBankInfo],
        "Informacoes do banco de dados",
        re.IGNORECASE,
    )


@pytest.mark.parametrize(
    ("key", "ocr_text"),
    (
        (I18nText.FastTravel, "Viagem Rapida"),
        (I18nText.Shorekeeper, "Guardia da Costa"),
        (I18nText.QuickSetup, "Configuragao rapida"),
        (I18nText.QuickSetup, "Configuragäo rápida"),
        (I18nText.EnemyHecate, "Hecate"),
        (I18nText.DataMergeCount, "Contagem de fusao de dados: 7"),
    ),
)
def test_portuguese_patterns_tolerate_observed_accent_ocr_loss(key, ocr_text):
    assert re.fullmatch(pt_regex(key), ocr_text, re.IGNORECASE)


def test_rapidocr_uses_the_bundled_latin_recognizer(monkeypatch):
    captured = {}

    class FakeRapidOCR:
        def __init__(self, *, params):
            captured.update(params)

    monkeypatch.setattr(rapidocr_util, "RapidOCR", FakeRapidOCR)
    rapidocr_util.create_ocr(latin=True)

    from rapidocr.utils.typings import LangRec

    assert captured["Rec.lang_type"] is LangRec.LATIN
    assert "Rec.lang_type" not in rapidocr_util._CPU_PARAMS


def test_rapidocr_service_selects_latin_for_portuguese(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        rapidocr_util,
        "create_ocr",
        lambda **kwargs: captured.update(kwargs) or object(),
    )
    context = SimpleNamespace(
        runtime=SimpleNamespace(cfg=SimpleNamespace(game=SimpleNamespace(device=Device.CPU))),
        spec=None,
    )
    window = SimpleNamespace(get_lang=lambda: Language.PT)

    RapidOcrServiceImpl(context, window, SimpleNamespace())

    assert captured == {"use_gpu": False, "latin": True}


def test_paddleocr_service_selects_portuguese_recognizer(monkeypatch):
    captured = {}
    fake_module = SimpleNamespace(
        create_paddleocr=lambda **kwargs: captured.update(kwargs) or object()
    )
    monkeypatch.setitem(sys.modules, "src.util.paddleocr_util", fake_module)
    import src.util

    monkeypatch.setattr(src.util, "paddleocr_util", fake_module, raising=False)
    context = SimpleNamespace(
        runtime=SimpleNamespace(cfg=SimpleNamespace(game=SimpleNamespace(device=Device.CPU))),
        spec=None,
    )
    window = SimpleNamespace(get_lang=lambda: Language.PT)

    PaddleOcrServiceImpl(context, window, SimpleNamespace())

    assert captured == {"use_gpu": False, "lang": "pt"}


def test_gui_task_spec_propagates_portuguese_to_legacy_rapidocr(monkeypatch):
    param_config = ParamConfig.build(
        content='{"Game":{"GameLanguage":"pt","GamePath":"Auto"}}'
    )
    spec = TaskSpec(
        param_config=param_config,
        game_lang=configured_game_language(param_config),
        ocr_use_gpu=False,
    )
    assert spec.game_lang is Language.PT

    from src.service import window_service as window_service_module

    monkeypatch.setattr(window_service_module.hwnd_util, "enable_dpi_awareness", lambda: None)
    monkeypatch.setattr(window_service_module.hwnd_util, "get_hwnds", lambda: [101])
    window = HwndServiceImpl(SimpleNamespace(spec=spec))
    assert window.get_lang() is Language.PT

    captured = {}
    monkeypatch.setattr(
        rapidocr_util,
        "create_ocr",
        lambda **kwargs: captured.update(kwargs) or object(),
    )
    context = SimpleNamespace(
        spec=spec,
        runtime=SimpleNamespace(cfg=SimpleNamespace(game=SimpleNamespace(device=Device.CPU))),
    )
    RapidOcrServiceImpl(context, window, SimpleNamespace())
    assert captured == {"use_gpu": False, "latin": True}
