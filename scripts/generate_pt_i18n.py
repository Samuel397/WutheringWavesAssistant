"""Generate the static Portuguese OCR inventory from official Wuthering Waves TextMaps.

The runtime must not read the large TextMap dump.  This tool joins the official
English/Simplified-Chinese and Portuguese ``MultiText.json`` files by ``Id`` and
prints the compact, reviewable dictionary fragment maintained in
``src/core/pt_i18n.py``.  The surrounding regex helpers remain hand-reviewed.

Usage::

    python scripts/generate_pt_i18n.py ../../candidate-wuwa-data/Textmaps
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.i18n import I18N_TEXT, I18nText, Language, RegexStr


NOISY_VALUES = {
    "Ocorreu um erro. Entre em contato com o SAC.",
    "Texto de teste",
    "placeholder",
}

# These values are still sourced from the Portuguese TextMap.  Overrides select
# the UI-specific value when an English label is reused in unrelated contexts.
OFFICIAL_OVERRIDES: dict[str, tuple[str, ...]] = {
    I18nText.WutheringWaves: ("Wuthering Waves  ",),
    I18nText.DailyTask: ("DailyTask",),
    I18nText.BossRushTask: ("BossRushTask",),
    I18nText.EchoMergeTask: ("EchoMergeTask",),
    I18nText.StoryTask: ("StoryTask",),
    I18nText.PickupTask: ("PickupTask",),
    I18nText.SoarToTheBeatMacroReplayTask: ("SoarToTheBeatMacroReplayTask",),
    I18nText.SoarToTheBeatMacroRecordTask: ("SoarToTheBeatMacroRecordTask",),
    # The upstream semantic label is not a literal TextMap entry.  The live
    # claim button uses the official generic Text_GetReward_Text translation.
    I18nText.CollectSupplies: ("Resgatar",),
    I18nText.Encore: ("Encore",),
    I18nText.Sanhua: ("Sanhua",),
    I18nText.Changli: ("Changli",),
    I18nText.XiangliYao: ("Xiangli Yao",),
    I18nText.Camellya: ("Camellya",),
    I18nText.Aemeath: ("Aemeath",),
    I18nText.EnemyDreamless: ("Insone",),
    I18nText.EnemySentryConstruct: ("Constructo de Sentinela",),
    I18nText.EnemyHecate: ("Hécate",),
    I18nText.EnemyDragonOfDirge: ("Dragão Lamentoso", "Dragão da Lamentação"),
    I18nText.EnemyReactorHusk: ("Reator Deteriorado",),
    I18nText.EnemyNightmareAdamSmasher: ("Pesadelo: Adam Smasher",),
    I18nText.EnemyMyriadSnareRustfireChassis: ("Prisão de Miríades: Corpo Decadente",),
    I18nText.PactOfNeonlightLeap: ("Pacto do Salto Neonluz",),
    I18nText.HaloOfStarryRadiance: ("Halo da Radiância Estelar",),
    I18nText.RiteOfGildedRevelation: ("Rito da Revelação Dourada",),
    I18nText.Jinzhou: ("Jinzhou",),
    I18nText.JinzhouCity: ("Cidade de Jinzhou", "Jinzhou"),
    I18nText.RoyaFrostlands: ("Terras Geladas de Roya", "Terras Geladas dos royanos"),
    I18nText.TapTheBlankAreaToClose: (
        "Toque na área em branco para fechar",
        "Toque na área vazia para fechar",
    ),
    I18nText.LuniteSubscriptionReward: (
        "Toque para resgatar a recompensa de Assinatura de Lunita de hoje",
        "Toque para resgatar as recompensas de hoje.",
    ),
    I18nText.Guidebook: ("Guia",),
    I18nText.PioneerPodcastUnavailable: (
        "Todos os canais do Podcast Pioneiro estão atualmente indisponíveis. "
        "Volte para a próxima edição quando o Podcast Pioneiro reabrir.",
    ),
    I18nText.PleaseSelectAtLeast5Echoes: ("Selecione ao menos 5 ecos",),
    I18nText.DataMergeCount: ("Contagem de fusão de dados: {0}",),
    I18nText.MaterialsSpots: ("Locais de Materiais",),
    I18nText.DoubleDropChancesToday: (
        "Chances de Saque Duplo Hoje:",
        "Chances de saque duplo hoje: {0}/{1}",
    ),
    I18nText.ClaimRewards: (
        "Coletar Recompensas",
        "Resgatar recompensas",
        "Resgate recompensas",
    ),
    I18nText.ChallengeAgain: ("Tentar Novamente", "Desafiar Novamente", "Reiniciar"),
    I18nText.SOL3Phase: ("Fase de SOL-3", "Fase de SOL3"),
    I18nText.Mail: ("Correio", "Correspondência"),
    I18nText.GuidebookJinzhou: ("Jinzhou", "Cidade de Jinzhou"),
    I18nText.ActivityDaily: ("Pts de atividade",),
    I18nText.Go: ("Ir",),
    I18nText.Challenge: ("Desafio",),
    I18nText.EnterTheForgeryChallenge: (
        'Entre no "Desafio da Forja"',
        'Entrar no "Desafio de Forja"',
        "Entre em Desafio de Forja",
    ),
    I18nText.DefeatTheEnemiesWithinTimeLimit: (
        "Derrote os inimigos no tempo estipulado: {q_count}/6",
        "Derrote os inimigos no tempo estipulado: {q_count}/5",
        "Derrote os inimigos no tempo estipulado: {q_count}/4",
    ),
    I18nText.ForgeryClaimX2: ("Resgatar ×2",),
    I18nText.ForgeryChallengeComplete: ("Desafio concluído", "Desafio completado"),
    I18nText.TacetField: ("Campo de Dissonância",),
    I18nText.TacetFieldChallengeComplete: ("Desafio concluído", "Desafio completado"),
    I18nText.TacetFieldNoticeChallengeComplete: ("Desafio concluído", "Desafio completado"),
    I18nText.DefeatTheTdsInTheTacetField: (
        "Derrote as DTs no Campo de Dissonância: {q_count}/{q_countMax}",
    ),
    I18nText.TacetFieldClaimX2: ("Resgatar ×2",),
    I18nText.RemainingWeeklyAttempts: (
        "Tentativas Restantes: {0}",
        "Tentativas Restantes Desta Semana",
    ),
    I18nText.ArrivingAtTheDestination: (
        "A chegada antecipada ao destino pode influenciar sua experiência na história. Confirma?",
    ),
    I18nText.WeeklySuggestedLv: ("Nível sugerido: {0}", "Nv. {0} sugerido"),
    I18nText.LimitedTimeEarlyAccess: (
        "Acesso antecipado temporário",
        "Acesso Antecipado por Tempo Limitado",
    ),
    I18nText.WeeklyBossHecate: ("Hécate",),
    I18nText.WeeklyBossCrownless: ("Insone",),
    I18nText.EnterTheSonoroSphere: ("Entre na Esfera Sonora", "Entrar na Esfera Sonora"),
    I18nText.WeeklySoloChallenge: ("Desafio Solo", "Desafio individual"),
    I18nText.YourCurrentSol3Phase: (
        "Sua Fase de SOL3 atual é significativamente maior que o nível recomendado "
        "para esta Esfera Sonora. Você NÃO obterá nenhum Eco. Deseja continuar mesmo assim?",
    ),
    I18nText.WeeklyDefeatTheEnemy: ("Derrote o inimigo", "Derrote Sigillum"),
    I18nText.WeeklyClaimRewards: (
        "Coletar Recompensas",
        "Resgatar recompensas",
        "Resgate recompensas",
    ),
    I18nText.YouHaveReachedTheChallengeLimit: (
        "Você atingiu o limite de desafios. Sair do desafio?",
    ),
    I18nText.TacetDiscordDefeated: (
        "Dissonâncias Transgressoras derrotadas: {击杀怪物数}/{怪物单日上限数}",
    ),
    I18nText.Deploy: ("Posicionar", "Implantar"),
    I18nText.StartChallenge: ("Iniciar desafio", "Inicie o desafio", "Inicie desafio"),
    I18nText.ClearTheTacetDiscordNest: (
        "Elimine o Ninho de Dissonância Transgressora",
        "Limpe o Ninho de Éterion",
    ),
    I18nText.TacetDiscordNestCleared: (
        "Ninho de Dissonância Transgressora Eliminado",
        "Ninho de Éterion Limpo",
    ),
    I18nText.ClearTheTacetDiscordNestMengzhou: (
        "Elimine o Ninho de Dissonância Transgressora",
        "Limpe o Ninho de Éterion",
    ),
    I18nText.TacetDiscordNestClearedMengzhou: (
        "Ninho de Dissonância Transgressora Eliminado",
        "Ninho de Éterion Limpo",
    ),
    I18nText.PdrStart: ("Iniciar Jogo", "Iniciar"),
    I18nText.PdrMax: ("MAX", "MÁX", "MÁXIMO"),
    I18nText.PdrSkip: ("Pular", "Ignorar"),
    I18nText.PdrChallengeFailed: (
        "Desafio falhou", "O desafio fracassou", "Falha no desafio", "Desafio não concluído",
    ),
    I18nText.PdrChallengeComplete: ("Desafio concluído", "Desafio completado"),
    I18nText.PdrReturn: ("Retornar",),
    I18nText.PdrResume: ("Continuar", "Retomar"),
    I18nText.ViewClaimRewards: (
        "Coletar Recompensas", "Resgatar recompensas", "Resgate recompensas",
    ),
    I18nText.ViewChallengeComplete: ("Desafio concluído", "Desafio completado"),
    I18nText.ViewChallengeFailed: (
        "Desafio falhou", "O desafio fracassou", "Falha no desafio", "Desafio não concluído",
    ),
    I18nText.ViewLeaveInstance2Leave: ("Sair",),
    I18nText.ViewTacetSuppressionChallengeComplete: (
        "Desafio concluído", "Desafio completado",
    ),
    I18nText.ViewTacetSuppressionClaimRewards: (
        "Coletar Recompensas", "Resgatar recompensas", "Resgate recompensas",
    ),
    I18nText.PdrCurrentPhase: ("Fase atual {0}/{1}",),
    I18nText.PdrRemainingDays5: ("Dias restantes: 5",),
    I18nText.ViewTacetSuppressionClaimX2: ("Resgatar ×2",),
    I18nText.ViewFight: ("Derrote o inimigo",),
}

# Not present in the extracted PT TextMap version.  They are unreleased/future
# resonator identifiers and must remain explicit instead of being guessed.
UNRESOLVED = {
    I18nText.Suoming: "not present in the official PT TextMap",
    I18nText.Jingran: "not present in the official PT TextMap",
    I18nText.Hsin: "not present in the official PT TextMap",
}


def _load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _index(rows: list[dict]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        content = row.get("Content")
        if content:
            result[content].append(str(row["Id"]))
    return result


def _clean(values: list[str]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        value = re.sub(r"<[^>]+>", "", value).strip()
        normalized = " ".join(value.casefold().split())
        if not value or len(value) > 180 or value in NOISY_VALUES or normalized in seen:
            continue
        seen.add(normalized)
        result.append(value)
    return tuple(result)


def resolve(textmaps: Path) -> tuple[dict[str, tuple[str, ...]], dict[str, str]]:
    en_rows = _load(textmaps / "en" / "multi_text" / "MultiText.json")
    zh_rows = _load(textmaps / "zh-Hans" / "multi_text" / "MultiText.json")
    pt_rows = _load(textmaps / "pt" / "multi_text" / "MultiText.json")
    pt_by_id = {str(row["Id"]): row.get("Content", "") for row in pt_rows}
    indexes = {"en": _index(en_rows), "zh": _index(zh_rows)}

    resolved: dict[str, tuple[str, ...]] = {}
    unresolved: dict[str, str] = dict(UNRESOLVED)
    for key, lang_map in I18N_TEXT.items():
        if key in OFFICIAL_OVERRIDES:
            resolved[key] = OFFICIAL_OVERRIDES[key]
            continue
        if key in unresolved:
            continue

        candidates: tuple[str, ...] = ()
        for lang_name, lang in (("en", Language.EN), ("zh", Language.ZH)):
            source = lang_map.get(lang)
            raw = source.raw if isinstance(source, RegexStr) else source
            if not raw:
                continue
            ids = indexes[lang_name].get(str(raw), ())
            candidates = _clean([pt_by_id.get(row_id, "") for row_id in ids])
            if candidates:
                break
        if candidates:
            resolved[key] = candidates
        else:
            unresolved[key] = "no exact EN/ZH TextMap Id match"
    return resolved, unresolved


def emit_python(resolved: dict[str, tuple[str, ...]], unresolved: dict[str, str]) -> None:
    print("PT_OFFICIAL_TEXT: dict[str, tuple[str, ...]] = {")
    for key, values in resolved.items():
        args = ", ".join(repr(value) for value in values)
        suffix = "," if len(values) == 1 else ""
        print(f"    {key!r}: ({args}{suffix}),")
    print("}")
    print()
    print("PT_I18N_UNRESOLVED = {")
    for key, reason in unresolved.items():
        print(f"    {key!r}: {reason!r},")
    print("}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("textmaps", type=Path)
    args = parser.parse_args()
    resolved, unresolved = resolve(args.textmaps)
    emit_python(resolved, unresolved)
    print(
        f"# resolved={len(resolved)} unresolved={len(unresolved)}",
    )


if __name__ == "__main__":
    main()
