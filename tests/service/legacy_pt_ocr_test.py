import ast
import re
from pathlib import Path

from src.core.pt_i18n import pt_fuzzy_regex
from src.service.auto_boss_service import OCR_NETWORK_TIMEOUT
from src.service.auto_pickup_service import PT_EXCLUSIVE_CHEST, _pt_pickup_pattern


ROOT = Path(__file__).resolve().parents[2]
SERVICE = ROOT / "src" / "service"


def _source(name: str) -> str:
    return (SERVICE / name).read_text(encoding="utf-8")


def _ocr_constants() -> dict[str, str]:
    tree = ast.parse(_source("page_event_service.py"))
    constants = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or not target.id.startswith("OCR_"):
            continue
        if not isinstance(node.value, ast.Call) or not isinstance(node.value.func, ast.Name):
            continue
        if node.value.func.id != "_ocr_exact":
            continue
        texts = [ast.literal_eval(argument) for argument in node.value.args]
        alternatives = [
            r"\s*".join(
                pt_fuzzy_regex(re.escape(part))
                for part in re.split(r"\s+", text.strip())
            )
            for text in texts
        ]
        constants[target.id] = rf"^(?:{'|'.join(alternatives)})$"
    return constants


def test_legacy_pt_ocr_constants_match_official_ui_text():
    constants = _ocr_constants()
    expected = {
        "OCR_CONFIRM": "Confirmar",
        "OCR_RESTART": "Reiniciar",
        "OCR_CLAIM_REWARDS": "Resgatar recompensas",
        "OCR_ABSORB": "Absorver",
        "OCR_FAST_TRAVEL": "Viagem rápida",
        "OCR_TEAM": "Equipe",
        "OCR_EVENTS": "Eventos",
        "OCR_MAP": "Mapa",
        "OCR_QUICK_SETUP": "Configuração rápida",
        "OCR_DO_NOT_SHOW_AGAIN": "Não mostrar novamente",
        "OCR_SWITCH_MAP": "Trocar mapa",
        "OCR_SEARCH": "Pesquisar",
        "OCR_DETECT": "Rastrear",
        "OCR_ENTER": "Entrar",
        "OCR_SOLO_CHALLENGE": "Desafio individual",
        "OCR_START_CHALLENGE": "Iniciar desafio",
        "OCR_SELECT_REVIVAL_ITEM": "Selecione um item de reavivamento",
    }
    for name, text in expected.items():
        assert re.fullmatch(constants[name], text, flags=re.IGNORECASE), (name, text)


def test_legacy_pt_ocr_accepts_observed_latin_model_substitutions():
    constants = _ocr_constants()
    expected = {
        "OCR_FAST_TRAVEL": "Viagem rapida",
        "OCR_QUICK_SETUP": "Configuragao rapida",
        "OCR_DO_NOT_SHOW_AGAIN": "Nao mostrar novamente",
    }
    for name, text in expected.items():
        assert re.fullmatch(constants[name], text, flags=re.IGNORECASE), (name, text)


def test_timeout_and_pickup_patterns_accept_official_and_deaccented_pt():
    official_timeout = (
        "Tempo de solicitação esgotado. Falha ao conectar ao servidor. "
        "Tente novamente mais tarde."
    )
    assert re.search(OCR_NETWORK_TIMEOUT, official_timeout, flags=re.IGNORECASE)
    assert re.search(
        OCR_NETWORK_TIMEOUT,
        "Tempo de solicitagao esgotado. Falha ao conectar ao servidor. Tente novamente mais tarde.",
        flags=re.IGNORECASE,
    )
    assert re.fullmatch(
        _pt_pickup_pattern("Baú de Suprimentos Básico"),
        "Bau de Suprimentos Basico",
        flags=re.IGNORECASE,
    )
    assert re.fullmatch(
        _pt_pickup_pattern("Patrimônio das Marés"),
        "Patrimonio das Mares",
        flags=re.IGNORECASE,
    )
    assert re.fullmatch(
        PT_EXCLUSIVE_CHEST,
        "Bau de Suprimentos Exclusivo",
        flags=re.IGNORECASE,
    )


def test_legacy_services_are_syntax_valid_and_wire_pt_matchers():
    sources = {
        name: _source(name)
        for name in (
            "page_event_service.py",
            "auto_boss_service.py",
            "auto_story_service.py",
            "auto_pickup_service.py",
        )
    }
    for name, source in sources.items():
        ast.parse(source, filename=name)

    assert "Toque para pousar em Solaris-3" in sources["auto_boss_service.py"]
    assert "OCR_DO_NOT_SHOW_AGAIN" in sources["auto_boss_service.py"]
    assert "Pular história" in sources["auto_story_service.py"]
    assert "OCR_CONFIRM" in sources["auto_story_service.py"]
    assert "resolve_resonator_ocr_name" in sources["page_event_service.py"]


def test_pickup_contains_official_pt_textmap_actions_and_chests():
    source = _source("auto_pickup_service.py")
    for text in (
        "Absorver",
        "Pegar",
        "Baú Suspeito",
        "Baú de Suprimentos Básico",
        "Baú de Suprimentos Padrão",
        "Baú de Suprimentos Avançado",
        "Baú de Suprimentos Exclusivo",
        "Baú de Suprimentos de Maré",
        "Patrimônio das Marés",
    ):
        assert text in source
