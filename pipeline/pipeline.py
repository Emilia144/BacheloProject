#!/usr/bin/env python3
"""
pipeline/pipeline.py
────────────────────
Reads pipeline/sources/*.xlsx  →  writes data/data.json

Sources combined for the 2026 dataset:
  general26.xlsx        general26 cohort     (n=107)
  BCG26.xlsx            BCG company cohort   (n=76)
  Regiocom26.xlsx       Regiocom cohort      (n=150)
  KühneUndNagel26.xlsx  K&N cohort           (n=13)

2024 productivity reference (for timeline chart only):
  general24.xlsx   col index 22 (0-based)
  BCG24.xlsx       col index 18 (0-based)

All four *26.xlsx files share an identical 24-column layout —
column positions are used directly rather than header-text matching.

Usage:
  cd "homepage2 - Copy"
  .venv/Scripts/python.exe pipeline/pipeline.py

Output:
  data/data.json   (created / overwritten)

Intermediate cross-tables are printed to stdout for every chart
section so you can verify against previously hardcoded values.
Discrepancies > 0.5 pp versus known reference values are flagged ⚠.

NOTE: The hero text and i18n.js say "310 Teilnehmer".  The source
files now total n=346, so all percentages will differ by ~1-3 pp
from earlier hardcoded values — this is expected growth in the survey.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Force UTF-8 stdout so Unicode box-drawing chars don't crash on Windows cp1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "pipeline" / "sources"
OUT  = ROOT / "data" / "data.json"

# ── Column indices (0-based) — identical across all four *26 files ────────────
#   Verified by header inspection — see session notes.
COL26_IDX = [10, 11, 12, 13, 14, 15, 19, 20, 21, 22, 23]
COL26_NAM = ['frequenz','zwecke','tools','kompetenz','prod_heute','prod_zukunft',
             'datenschutz','strategisch','phase','herausforderung','modellstrategie']

# ── Fixed category orders (determine JSON array positions) ────────────────────
KOMP_ORDER  = ['Ausprobiert','Einfache Prompts','Modelle & Prompting',
               'Erweiterte Funktionen','Eigene Lösungen','Eigene Modelle']
PHASE_ORDER = ['Phase 1','Phase 2','Phase 3','Phase 4']
STRAT_ORDER = ['Effizienzhebel','Gleichermaßen beides','Wachstumstreiber','Bisher weder noch']
PROD_ORDER  = ['Negativ','Keine Änderung','Leichte Verbesserung','Deutliche Verbesserung']
# 3-bar version: bottom two categories merged (used in comparative cmp-rows and report timeline)
PROD_ORDER_3 = ['Deutliche Verbesserung','Leichte Verbesserung','Keine / Negative Änderung']
# Challenge order: sorted by Phase-1 frequency descending (ROI > Governance > Data > IT > Personnel)
CHAL_ORDER  = [
    'Unklarer Business Case / ROI-Nachweis',
    'Unklare Governance und regulatorische Unsicherheit',
    'Fehlende Datenqualität und -verfügbarkeit',
    'Integration in bestehende IT-Systeme',
    'Mangel an qualifiziertem Personal und Know-how',
]

# ── Hardcoded reference values for discrepancy detection ─────────────────────
# NOTE: survey grew from n=310 to n=346; old n=310 refs removed.
# BCG-specific refs (from vergleich.html hardcoded values) used in build_comparative().
REFS: dict = {}  # kept for flag() compatibility; populated per-section below


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_26(fname: str) -> pd.DataFrame:
    df = pd.read_excel(SRC / fname, sheet_name=0, engine='openpyxl', header=0)
    df = df.iloc[:, COL26_IDX].copy()
    df.columns = COL26_NAM
    return df


def map_series(series: pd.Series, mapping: dict) -> pd.Series:
    """Map values by substring match (first match wins, case-insensitive)."""
    def _map(v):
        if pd.isna(v):
            return None
        s = str(v).lower()
        for key, label in mapping.items():
            if key.lower() in s:
                return label
        return None
    return series.map(_map)


def crosstab_pct(rows: pd.Series, cols: pd.Series,
                 row_order: list, col_order: list,
                 normalize: str = 'columns') -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cross-tabulate rows×cols, reindex to fixed orders, return (raw, pct)."""
    ct  = pd.crosstab(rows, cols)
    ct  = ct.reindex(row_order, fill_value=0)
    ct  = ct.reindex(columns=[c for c in col_order if c in ct.columns or True],
                     fill_value=0)
    # Ensure all expected columns are present
    for c in col_order:
        if c not in ct.columns:
            ct[c] = 0
    ct = ct[col_order]
    raw = ct.copy()
    if normalize == 'columns':
        pct_df = ct.div(ct.sum(axis=0), axis=1).mul(100).round(1).fillna(0.0)
    else:  # rows
        pct_df = ct.div(ct.sum(axis=1), axis=0).mul(100).round(1).fillna(0.0)
    return raw, pct_df


def flag(label: str, computed: float, ref_key: str | None = None,
         threshold: float = 0.5) -> None:
    """Print the computed value; flag if it differs from reference by > threshold pp."""
    if ref_key and ref_key in REFS:
        ref = REFS[ref_key]
        diff = abs(computed - ref)
        marker = f"  ⚠  |Δ| = {diff:.1f} pp  (ref = {ref:.1f}%)" if diff > threshold else ""
        print(f"    {label}: {computed:.1f}%{marker}")
    else:
        print(f"    {label}: {computed:.1f}%")


# ── Load & combine 2026 data ──────────────────────────────────────────────────

print("=" * 70)
print("Loading 2026 sources")
print("=" * 70)
dfs: list[pd.DataFrame] = []
for fname in ['general26.xlsx', 'BCG26.xlsx', 'Regiocom26.xlsx', 'KühneUndNagel26.xlsx']:
    d = load_26(fname)
    print(f"  {fname:<30} {len(d):>4} rows")
    dfs.append(d)
df26 = pd.concat(dfs, ignore_index=True)
N = len(df26)
print(f"  {'COMBINED':<30} {N:>4} rows  (note: hero text says 310 — survey grew)\n")

# Label normalisation
df26['k_label'] = map_series(df26['kompetenz'], {
    'ausprobiert':        'Ausprobiert',
    'einfache Prompts':   'Einfache Prompts',
    'verschiedene Modelle': 'Modelle & Prompting',
    'erweiterte Funktionen': 'Erweiterte Funktionen',
    'eigene GenAI-basierte': 'Eigene Lösungen',
    'eigene Modelle':     'Eigene Modelle',
})
df26['p_label'] = map_series(df26['phase'], {
    'Konzeption':      'Phase 1',
    'Prototyp':        'Phase 2',
    'Produktivversion':'Phase 3',
    'Rollout':         'Phase 4',
})
df26['s_label'] = map_series(df26['strategisch'], {
    'Effizienzhebel':   'Effizienzhebel',
    'Gleicherma':       'Gleichermaßen beides',   # matches "Gleichermaßen beides"
    'Wachstumstreiber': 'Wachstumstreiber',
    'weder noch':       'Bisher weder noch',
})
df26['ph_label'] = map_series(df26['prod_heute'], {
    'Negative': 'Negativ',
    'Keine':    'Keine Änderung',   # covers "Keine Änderung" + "Keine Einschätzung möglich"
    'Leichte':  'Leichte Verbesserung',
    'Deutliche':'Deutliche Verbesserung',
})
df26['pf_label'] = map_series(df26['prod_zukunft'], {
    'Negative': 'Negativ',
    'Keine':    'Keine Änderung',
    'Leichte':  'Leichte Verbesserung',
    'Deutliche':'Deutliche Verbesserung',
})

# ── 2024 productivity data (for timeline chart only) ─────────────────────────

def _map_prod(v) -> str | None:
    if pd.isna(v):
        return None
    s = str(v)
    if 'Negative' in s: return 'Negativ'
    if 'Keine'    in s: return 'Keine Änderung'
    if 'Leichte'  in s: return 'Leichte Verbesserung'
    if 'Deutliche' in s: return 'Deutliche Verbesserung'
    return None

df24_g = pd.read_excel(SRC / 'general24.xlsx', sheet_name=0, engine='openpyxl',
                       usecols=[22], header=0)
df24_g.columns = ['prod']
df24_b = pd.read_excel(SRC / 'BCG24.xlsx', sheet_name=0, engine='openpyxl',
                       usecols=[18], header=0)
df24_b.columns = ['prod']
df24 = pd.concat([df24_g, df24_b], ignore_index=True)
df24['prod_label'] = df24['prod'].map(_map_prod)
n24 = df24['prod_label'].notna().sum()
print(f"2024 productivity data: {n24} valid responses out of {len(df24)} rows\n")


# ═════════════════════════════════════════════════════════════════════════════
#  Chart builders
# ═════════════════════════════════════════════════════════════════════════════

def build_challenges_by_stage() -> dict:
    """
    challengesChart  — multi-line, x-axis = phases, datasets = challenges.
    pct_data[challenge_idx][phase_idx] = % of respondents in that phase
    who cite that challenge as their primary barrier.
    """
    print("=" * 70)
    print("CHART: challenges_by_stage")
    print("=" * 70)

    sub = df26.dropna(subset=['herausforderung', 'p_label'])
    raw, pct_df = crosstab_pct(
        sub['p_label'], sub['herausforderung'],
        PHASE_ORDER, CHAL_ORDER, normalize='rows'
    )
    print("  RAW counts  (rows = phase, cols = challenge):")
    print(raw.to_string()); print()
    print("  PCT  (row-normalised per phase — % citing each challenge):")
    print(pct_df.to_string()); print()

    # i18n keys — all exist in i18n.js
    PHASE_KEYS = [
        'results2026.findings.maturity.p1.name',
        'results2026.findings.maturity.p2.name',
        'results2026.findings.maturity.p3.name',
        'results2026.findings.maturity.p4.name',
    ]
    CHAL_I18N = [
        'results2026.findings.challenges.roi',
        'results2026.findings.challenges.governance',
        'results2026.findings.challenges.data',
        'results2026.findings.challenges.it',
        'results2026.findings.challenges.personnel',
    ]
    # Distinct colors for 5 challenge lines
    CHAL_COLORS = ['#1565C0', '#3F7DBF', '#90CAF9', '#BEBEBE', '#004A99']

    datasets = []
    for key, color, chal in zip(CHAL_I18N, CHAL_COLORS, CHAL_ORDER):
        values = [round(float(pct_df.loc[ph, chal]), 1) for ph in PHASE_ORDER]
        datasets.append({'label_i18n': key, 'values': values, 'color': color})

    return {'labels': PHASE_KEYS, 'datasets': datasets}


def build_stacked_proficiency() -> dict:
    """
    stackedTodayChart + stackedFutureChart
    x-axis = 6 proficiency levels (KOMP_ORDER)
    pct_data rows = 4 productivity categories (PROD_ORDER)
    Each column (proficiency level) normalises to 100 %.
    """
    print("=" * 70)
    print("CHART: stacked_proficiency")
    print("=" * 70)

    # NOTE: 'results2026.findings.productivity.negative' does not yet exist
    # in i18n.js — add it alongside the existing productivity keys.
    CAT_KEYS = [
        'results2026.findings.productivity.negative',   # ← add to i18n.js
        'results2026.findings.productivity.none',
        'results2026.findings.productivity.slight',
        'results2026.findings.productivity.significant',
    ]
    PROF_KEYS = [
        'results2026.findings.proficiency.level1',
        'results2026.findings.proficiency.level2',
        'results2026.findings.proficiency.level3',
        'results2026.findings.proficiency.level4',
        'results2026.findings.proficiency.level5',
        'results2026.findings.proficiency.level6',
    ]

    def _make_subset(prod_col: str, label: str) -> dict:
        print(f"\n  ── {label} ──")
        sub = df26.dropna(subset=['k_label', prod_col])
        raw, pct_df = crosstab_pct(
            sub[prod_col], sub['k_label'],
            PROD_ORDER, KOMP_ORDER, normalize='columns'
        )
        print("  RAW  (rows = prod category, cols = proficiency level):")
        print(raw.to_string())
        print("  PCT  (col-normalised — each proficiency level sums to 100):")
        print(pct_df.to_string()); print()

        pct_data = [
            [round(float(pct_df.loc[cat, lev]), 1) for cat in PROD_ORDER]
             for lev in KOMP_ORDER
        ]
        raw_data = [
            [int(raw.loc[cat, lev]) for lev in KOMP_ORDER]
            for cat in PROD_ORDER
        ]
        return {
            'labels_i18n':          PROF_KEYS,
            'pct_data':             pct_data,
            'raw_data':             raw_data,
            'category_labels_i18n': CAT_KEYS,
        }

    return {
        'today':  _make_subset('ph_label', 'TODAY  (prod_heute)'),
        'future': _make_subset('pf_label', 'FUTURE (prod_zukunft)'),
    }


def build_growth_by_phase() -> dict:
    """
    growthEfficiencyChart  — multi-line, x-axis = phases.
    pct_data[cat_idx][phase_idx] = % of respondents in that phase
    who see GenAI as that strategic category.
    Row order: STRAT_ORDER = [Effizienz, Beides, Wachstum, WederNoch]
    """
    print("=" * 70)
    print("CHART: growth_by_phase")
    print("=" * 70)

    sub = df26.dropna(subset=['s_label', 'p_label'])
    raw, pct_df = crosstab_pct(
        sub['s_label'], sub['p_label'],
        STRAT_ORDER, PHASE_ORDER, normalize='columns'
    )
    print("  RAW:")
    print(raw.to_string())
    print("  PCT  (col-normalised — each phase column sums to 100):")
    print(pct_df.to_string()); print()

    PHASE_KEYS = [
        'results2026.findings.maturity.p1.name',
        'results2026.findings.maturity.p2.name',
        'results2026.findings.maturity.p3.name',
        'results2026.findings.maturity.p4.name',
    ]
    pct_data   = [[round(float(pct_df.loc[cat, ph]), 1) for ph in PHASE_ORDER]
                  for cat in STRAT_ORDER]
    raw_counts = [[int(raw.loc[cat, ph]) for ph in PHASE_ORDER]
                  for cat in STRAT_ORDER]

    return {'labels_i18n': PHASE_KEYS, 'pct_data': pct_data, 'raw_counts': raw_counts}


def build_growth_by_proficiency() -> dict:
    """
    growthEfficiencyProficiencyChart  — stacked bar, x-axis = proficiency levels.
    Same row order as growth_by_phase.
    """
    print("=" * 70)
    print("CHART: growth_by_proficiency")
    print("=" * 70)

    sub = df26.dropna(subset=['s_label', 'k_label'])
    raw, pct_df = crosstab_pct(
        sub['s_label'], sub['k_label'],
        STRAT_ORDER, KOMP_ORDER, normalize='columns'
    )
    print("  RAW:")
    print(raw.to_string())
    print("  PCT  (col-normalised — each proficiency level sums to 100):")
    print(pct_df.to_string())
    print("  ⚠ 'Eigene Modelle' has n=8 — treat as trend indicator only.\n")

    PROF_KEYS = [
        'results2026.findings.proficiency.level1',
        'results2026.findings.proficiency.level2',
        'results2026.findings.proficiency.level3',
        'results2026.findings.proficiency.level4',
        'results2026.findings.proficiency.level5',
        'results2026.findings.proficiency.level6',
    ]
    pct_data   = [[round(float(pct_df.loc[cat, lev]), 1) for lev in KOMP_ORDER]
                  for cat in STRAT_ORDER]
    raw_counts = [[int(raw.loc[cat, lev]) for lev in KOMP_ORDER]
                  for cat in STRAT_ORDER]

    return {'labels_i18n': PROF_KEYS, 'pct_data': pct_data, 'raw_counts': raw_counts}


def build_productivity_timeline() -> dict:
    """
    productivityChart  — line chart, 3 x-axis points, 4 dataset lines.
    x[0] = 2024/25 (historical)
    x[1] = 2026 heute  (forecast_from_index = 1  → divider falls between x[1] and x[2])
    x[2] = 2026 in 1–3 J. (forecast zone, shaded)
    """
    print("=" * 70)
    print("CHART: productivity_timeline")
    print("=" * 70)

    def _dist(series: pd.Series) -> dict:
        s = series.dropna()
        n = len(s)
        return {cat: round((s == cat).sum() / n * 100, 1) if n else 0.0
                for cat in PROD_ORDER}

    p24  = _dist(df24['prod_label'])
    p26h = _dist(df26['ph_label'])
    p26f = _dist(df26['pf_label'])
    n26h = df26['ph_label'].notna().sum()
    n24v = df24['prod_label'].notna().sum()

    # Merge bottom 2 → 3-bar layout
    p24_merged  = round(p24['Negativ']  + p24['Keine Änderung'],  1)
    p26h_merged = round(p26h['Negativ'] + p26h['Keine Änderung'], 1)
    p26f_merged = round(p26f['Negativ'] + p26f['Keine Änderung'], 1)

    print(f"  {'Category':<32} {'2024/25':>10} {'2026 heute':>10} {'2026 1-3J':>10}")
    print("  " + "─" * 60)
    for cat in ['Deutliche Verbesserung', 'Leichte Verbesserung']:
        print(f"  {cat:<32} {p24[cat]:>10.1f} {p26h[cat]:>10.1f} {p26f[cat]:>10.1f}")
    print(f"  {'Keine / Negative (merged)':<32} {p24_merged:>10.1f} {p26h_merged:>10.1f} {p26f_merged:>10.1f}")
    print(f"  {'n (valid responses)':<32} {n24v:>10} {n26h:>10} {n26h:>10}")
    print()

    pos_today  = round(p26h['Leichte Verbesserung'] + p26h['Deutliche Verbesserung'], 1)
    pos_future = round(p26f['Leichte Verbesserung'] + p26f['Deutliche Verbesserung'], 1)
    flag('Deutliche Verbesserung  2026h', p26h['Deutliche Verbesserung'])
    flag('Deutliche Verbesserung  2026f', p26f['Deutliche Verbesserung'])
    flag('Positive total          2026h', pos_today)
    flag('Positive total          2026f', pos_future)
    print()

    # 3-category datasets (Negativ + Keine Änderung merged)
    datasets_def = [
        # (i18n key,                                         label,                        values,                                                         color,           border_dash)
        ('results2026.findings.productivity.significant', 'Deutliche Verbesserung',
         [p24['Deutliche Verbesserung'], p26h['Deutliche Verbesserung'], p26f['Deutliche Verbesserung']], 'var(--th-blue)', None),
        ('results2026.findings.productivity.slight',      'Leichte Verbesserung',
         [p24['Leichte Verbesserung'],   p26h['Leichte Verbesserung'],   p26f['Leichte Verbesserung']],   '#90CAF9',        None),
        ('results2026.findings.productivity.none_neg',    'Keine / Negative Änderung',
         [p24_merged,                    p26h_merged,                    p26f_merged],                    '#BEBEBE',        [5, 4]),
    ]
    datasets = []
    for i18n_key, _label, values, color, dash in datasets_def:
        ds: dict = {'label_i18n': i18n_key, 'values': values, 'color': color}
        if dash:
            ds['border_dash'] = dash
        datasets.append(ds)

    return {
        'labels': ['2024\u2009/\u200925', '2026\u2009(heute)', '2026\u2009(in\u00a01\u20133\u00a0J.)'],
        'forecast_from_index': 1,
        'datasets': datasets,
    }


# ═════════════════════════════════════════════════════════════════════════════
#  Component builders  (renderProgressList / renderIconList items)
# ═════════════════════════════════════════════════════════════════════════════

def build_components() -> dict:
    print("=" * 70)
    print("COMPONENTS")
    print("=" * 70)

    freq_vc = df26['frequenz'].value_counts()
    ms_vc   = df26['modellstrategie'].value_counts()
    ds_vc   = df26['datenschutz'].value_counts()
    st_vc   = df26['strategisch'].value_counts()

    # ── usage_frequency ──────────────────────────────────────────────────────
    FREQ_DEF = [
        ('Täglich',     'results2026.findings.usage.daily',   'var(--th-blue)'),
        ('Wöchentlich', 'results2026.findings.usage.weekly',  '#42A5F5'),
        ('Selten',      'results2026.findings.usage.rarely',  '#90CAF9'),
        ('Gar nicht',   'results2026.findings.usage.never',   '#BEBEBE'),
    ]
    print("\n  usage_frequency:")
    usage_frequency = []
    for cat, key, color in FREQ_DEF:
        c = int(freq_vc.get(cat, 0))
        v = round(c / N * 100, 1)
        print(f"    {cat:<14} n={c:3d}/{N}  {v:.1f}%")
        usage_frequency.append({
            'label_i18n': key, 'value': v, 'color': color,
            'displayValue': f'{v}\u00a0%',
        })

    # ── model_strategy (progress bars) ───────────────────────────────────────
    # i18n keys exist in i18n.js under results2026.dash.q15.*
    MS_DEF = [
        ('Hybridansatz',    'results2026.dash.q15.hybrid',      'var(--th-blue)'),
        ('Spezialisierte, kleinere',  'results2026.dash.q15.specialized',  '#42A5F5'),
        ('Kann ich nicht',  'results2026.dash.q15.uncertain',    '#BEBEBE'),
        ('Mehrere große',   'results2026.dash.q15.multiple',     '#90CAF9'),
        ('Ein zentrales',   'results2026.dash.q15.universal',    '#D32F2F'),
    ]
    print("\n  model_strategy (progress bars):")
    model_strategy = []
    n_ms = int(ms_vc.sum())
    for frag, key, color in MS_DEF:
        cat = next((k for k in ms_vc.index if frag.lower() in str(k).lower()), None)
        c = int(ms_vc.get(cat, 0)) if cat is not None else 0
        v = round(c / n_ms * 100, 1)
        print(f"    {frag:<20} n={c:3d}  {v:.1f}%")
        model_strategy.append({
            'label_i18n': key, 'value': v, 'color': color,
            'displayValue': f'{v}\u00a0%',
        })

    # ── privacy_compliance ───────────────────────────────────────────────────
    # No existing i18n keys → added in i18n.js as results2026.privacy.*
    DS_DEF = [
        ('konsequent auf deren',    'results2026.privacy.konsequent',  '#1565C0'),
        ('besten Gewissens',        'results2026.privacy.bestEffort',  '#42A5F5'),
        ('nicht immer konsequent',  'results2026.privacy.notAlways',   '#FF9800'),
        ('keine konkreten Regeln',  'results2026.privacy.noRules',     '#D32F2F'),
    ]
    print("\n  privacy_compliance:")
    privacy_compliance = []
    n_ds = int(ds_vc.sum())
    for frag, key, color in DS_DEF:
        cat = next((k for k in ds_vc.index if frag.lower() in str(k).lower()), None)
        c = int(ds_vc.get(cat, 0)) if cat is not None else 0
        v = round(c / n_ds * 100, 1)
        print(f"    {frag[:32]:<32} n={c:3d}  {v:.1f}%")
        privacy_compliance.append({
            'label_i18n': key, 'value': v, 'color': color,
            'displayValue': f'{v}\u00a0%',
        })

    # ── strategic_direction ──────────────────────────────────────────────────
    # These keys are referenced in growth-efficiency.js but not yet in i18n.js.
    # Add them there: growthEfficiency.cat.{efficiency,both,growth,neither}
    ST_DEF = [
        ('Effizienzhebel',  'growthEfficiency.cat.efficiency', '#004A99'),
        ('Gleicherma',      'growthEfficiency.cat.both',
         # Gradient for "both" — matches the original striped pattern in the report view
         'repeating-linear-gradient(-45deg,#004A99 0,#004A99 2px,#90CAF9 2px,#90CAF9 8px)'),
        ('Wachstumstreiber','growthEfficiency.cat.growth',     '#90CAF9'),
        ('weder noch',      'growthEfficiency.cat.neither',    '#BEBEBE'),
    ]
    print("\n  strategic_direction:")
    strategic_direction = []
    n_st = int(st_vc.sum())
    for frag, key, color in ST_DEF:
        cat = next((k for k in st_vc.index if frag.lower() in str(k).lower()), None)
        c = int(st_vc.get(cat, 0)) if cat is not None else 0
        v = round(c / n_st * 100, 1)
        print(f"    {frag:<20} n={c:3d}  {v:.1f}%")
        strategic_direction.append({
            'label_i18n': key, 'value': v, 'color': color,
            'displayValue': f'{v}\u00a0%',
        })

    # ── q15_icons (icon-list, dashboard view) ────────────────────────────────
    # Same model-strategy data, icon-list format.
    # icon names: Lucide icon set (https://lucide.dev/icons/)
    Q15_DEF = [
        ('Hybridansatz',   'results2026.dash.q15.hybrid',      'git-merge',   True),
        ('Spezialisierte, kleinere', 'results2026.dash.q15.specialized',  'crosshair',   False),
        ('Kann ich nicht', 'results2026.dash.q15.uncertain',    'help-circle', False),
        ('Mehrere große',  'results2026.dash.q15.multiple',     'cpu',         False),
        ('Ein zentrales',  'results2026.dash.q15.universal',    'globe',       False),
    ]
    q15_icons = []
    for frag, key, icon, highlight in Q15_DEF:
        cat = next((k for k in ms_vc.index if frag.lower() in str(k).lower()), None)
        c = int(ms_vc.get(cat, 0)) if cat is not None else 0
        v = round(c / n_ms * 100, 1)
        q15_icons.append({
            'icon': icon, 'label_i18n': key,
            'value': f'{v}\u00a0%', 'highlight': highlight,
        })

    return {
        'usage_frequency':    usage_frequency,
        'model_strategy':     model_strategy,
        'privacy_compliance': privacy_compliance,
        'strategic_direction':strategic_direction,
        'q15_icons':          q15_icons,
    }


# ═════════════════════════════════════════════════════════════════════════════
#  Comparative builder  (per-company sections for data.json["comparative"])
# ═════════════════════════════════════════════════════════════════════════════

# Short display labels used in challenge ranking (match vergleich.html data-cat attrs)
_CHAL_CATS: dict[str, str] = {
    'roi':   'Unklarer Business Case / ROI-Nachweis',
    'it':    'Integration in bestehende IT-Systeme',
    'gov':   'Unklare Governance und regulatorische Unsicherheit',
    'data':  'Fehlende Datenqualität und -verfügbarkeit',
    'staff': 'Mangel an qualifiziertem Personal und Know-how',
}
_CHAL_SHORT: dict[str, str] = {
    'roi':   'Unklarer ROI-Nachweis',
    'it':    'IT-Integration',
    'gov':   'Governance & Regulatorik',
    'data':  'Datenqualität',
    'staff': 'Qualifiziertes Personal',
}

_TOOLS_DEF = [
    ('ChatGPT', 'OpenAI ChatGPT'),
    ('Copilot', 'Microsoft Copilot'),
    ('Gemini',  'Google Gemini'),
    ('Claude',  'Anthropic Claude'),
]

# BCG reference values extracted from vergleich.html for discrepancy checks
_BCG_REFS: dict[str, object] = {
    'kpis': {
        'adoption': 100.0, 'daily_usage': 90.8,
        'productivity_positive': 96.1, 'in_production': 63.1, 'strategic_lever': 96.1,
    },
    'usage_frequency': {'Täglich': 90.8, 'Wöchentlich': 7.9, 'Selten': 1.3, 'Gar nicht': 0.0},
    'tools': {'OpenAI ChatGPT': 98.7, 'Microsoft Copilot': 25.0,
              'Google Gemini': 14.5, 'Anthropic Claude': 9.2},
    'prod_today':  [47.4, 48.7, 3.9],   # Deutliche, Leichte, Keine/Neg
    'prod_future': [81.6, 15.8, 2.6],
    'phase': [14.5, 22.4, 36.8, 26.3],  # P1..P4
    'challenges': {'data': 27.6, 'roi': 26.3, 'it': 22.4, 'staff': 13.2, 'gov': 10.5},
    'proficiency': [1.3, 22.4, 47.4, 19.7, 7.9, 1.3],  # KOMP_ORDER
    'privacy': [43.4, 44.7, 9.2, 2.6],
    'growth_eff': {'Effizienzhebel': 56.6, 'Gleichermaßen beides': 23.7,
                   'Wachstumstreiber': 15.8, 'Bisher weder noch': 3.9},
    'timeline': {
        'Deutliche Verbesserung':    [40.8, 47.4, 81.6],
        'Leichte Verbesserung':      [59.2, 48.7, 15.8],
        'Keine / Negative Änderung': [11.7,  3.9,  2.6],
    },
}


def build_comparative() -> dict:
    """
    Build per-company comparative data for data.json["comparative"].
    Reuses load_26(), map_series(), crosstab_pct(), flag(), and all *_ORDER constants.
    """
    print("=" * 70)
    print("COMPARATIVE: per-company sections")
    print("=" * 70)

    def _label(df: pd.DataFrame) -> pd.DataFrame:
        """Apply all label normalisations — same mappings as used on df26."""
        df = df.copy()
        df['k_label'] = map_series(df['kompetenz'], {
            'ausprobiert':            'Ausprobiert',
            'einfache Prompts':       'Einfache Prompts',
            'verschiedene Modelle':   'Modelle & Prompting',
            'erweiterte Funktionen':  'Erweiterte Funktionen',
            'eigene GenAI-basierte':  'Eigene Lösungen',
            'eigene Modelle':         'Eigene Modelle',
        })
        df['p_label'] = map_series(df['phase'], {
            'Konzeption':       'Phase 1',
            'Prototyp':         'Phase 2',
            'Produktivversion': 'Phase 3',
            'Rollout':          'Phase 4',
        })
        df['s_label'] = map_series(df['strategisch'], {
            'Effizienzhebel':   'Effizienzhebel',
            'Gleicherma':       'Gleichermaßen beides',
            'Wachstumstreiber': 'Wachstumstreiber',
            'weder noch':       'Bisher weder noch',
        })
        df['ph_label'] = map_series(df['prod_heute'], {
            'Negative': 'Negativ', 'Keine': 'Keine Änderung',
            'Leichte': 'Leichte Verbesserung', 'Deutliche': 'Deutliche Verbesserung',
        })
        df['pf_label'] = map_series(df['prod_zukunft'], {
            'Negative': 'Negativ', 'Keine': 'Keine Änderung',
            'Leichte': 'Leichte Verbesserung', 'Deutliche': 'Deutliche Verbesserung',
        })
        return df

    def _prod3(series: pd.Series) -> list[dict]:
        """3-bar productivity distribution (Negativ + Keine Änderung merged)."""
        s = series.dropna()
        total = len(s)
        if total == 0:
            return [{'label': l, 'value': 0.0} for l in PROD_ORDER_3]
        deut   = int((s == 'Deutliche Verbesserung').sum())
        leich  = int((s == 'Leichte Verbesserung').sum())
        merged = int((s == 'Negativ').sum()) + int((s == 'Keine Änderung').sum())
        return [
            {'label': 'Deutliche Verbesserung',    'value': round(deut   / total * 100, 1)},
            {'label': 'Leichte Verbesserung',       'value': round(leich  / total * 100, 1)},
            {'label': 'Keine / Negative Änderung',  'value': round(merged / total * 100, 1)},
        ]

    def _merge3_dict(d: dict) -> dict:
        return {
            'Deutliche Verbesserung':    d['Deutliche Verbesserung'],
            'Leichte Verbesserung':      d['Leichte Verbesserung'],
            'Keine / Negative Änderung': round(d['Negativ'] + d['Keine Änderung'], 1),
        }

    def _chk(label: str, computed: float, ref: float | None) -> None:
        if ref is None:
            return
        diff = abs(computed - ref)
        marker = f'  ⚠  |Δ| = {diff:.1f} pp  (ref = {ref:.1f}%)' if diff > 0.5 else ''
        print(f"      {label:<35} {computed:.1f}%{marker}")

    # ── Pre-compute benchmark distributions (df26, already labelled) ──────────
    bench_prod_today  = _prod3(df26['ph_label'])
    bench_prod_future = _prod3(df26['pf_label'])

    # n_bench_users: respondents who answered the tools question
    n_bench_tools = int(df26['tools'].notna().sum())
    tools_series_bench = df26['tools'].dropna()
    bench_tools_vals: dict[str, float] = {}
    for frag, display in _TOOLS_DEF:
        c = int(tools_series_bench.str.contains(frag, case=False, na=False).sum())
        bench_tools_vals[display] = round(c / n_bench_tools * 100, 1) if n_bench_tools else 0.0

    chal_vc_bench = df26['herausforderung'].value_counts()
    n_chal_bench  = int(chal_vc_bench.sum())
    bench_challenges: list[dict] = []
    for cat_key, full_label in _CHAL_CATS.items():
        c = int(chal_vc_bench.get(full_label, 0))
        if c == 0:
            c = sum(v for k, v in chal_vc_bench.items()
                    if full_label[:20].lower() in str(k).lower())
        bench_challenges.append({
            'cat': cat_key,
            'label': _CHAL_SHORT[cat_key],
            'value': round(c / n_chal_bench * 100, 1) if n_chal_bench else 0.0,
        })
    bench_challenges_ranked = sorted(bench_challenges, key=lambda x: -x['value'])

    print(f"  Benchmark tools respondents (n_bench_users): {n_bench_tools}  "
          f"(was hardcoded as 283 for n=310 dataset)")
    print(f"  Benchmark challenge n: {n_chal_bench}")

    COMPANIES = [
        {
            'key': 'bcg', 'file26': 'BCG26.xlsx',
            'file24': 'BCG24.xlsx', 'col24_prod': 18,
            'has_longitudinal': True,
            'display': 'BCG', 'industry_i18n': 'cmp.meta.industry.consulting',
        },
        {
            'key': 'regiocom', 'file26': 'Regiocom26.xlsx',
            'file24': 'Regiocom24.xlsx', 'col24_prod': None,   # detect from headers
            'has_longitudinal': (SRC / 'Regiocom24.xlsx').exists(),
            'display': 'Regiocom', 'industry_i18n': 'cmp.meta.industry.it_services',
        },
        {
            'key': 'kuehnenagl', 'file26': 'KühneUndNagel26.xlsx',
            'file24': None, 'col24_prod': None,
            'has_longitudinal': False,
            'display': 'Kühne und Nagel', 'industry_i18n': 'cmp.meta.industry.logistics',
        },
    ]

    result: dict = {}

    for comp in COMPANIES:
        ckey   = comp['key']
        is_bcg = ckey == 'bcg'
        print(f"\n{'─' * 70}")
        print(f"COMPANY: {comp['display']}  ({ckey})")
        print(f"{'─' * 70}")

        df_c = _label(load_26(comp['file26']))
        N_C  = len(df_c)
        print(f"  n = {N_C}")

        # ── KPIs ─────────────────────────────────────────────────────────────
        print("\n  KPIs:")
        gar_mask  = df_c['frequenz'].str.contains('Gar nicht', case=False, na=True)
        n_adopt   = int((~gar_mask).sum())
        kpi_adopt = round(n_adopt / N_C * 100, 1)
        b_adopt   = round((~df26['frequenz'].str.contains('Gar nicht', case=False, na=True)).sum() / N * 100, 1)

        daily_mask = df_c['frequenz'].str.contains('Täglich', case=False, na=False)
        kpi_daily  = round(daily_mask.sum() / N_C * 100, 1)
        b_daily    = round(df26['frequenz'].str.contains('Täglich', case=False, na=False).sum() / N * 100, 1)

        ph_c = df_c['ph_label'].dropna()
        kpi_prod_pos = round(ph_c.isin(['Leichte Verbesserung', 'Deutliche Verbesserung']).sum() / len(ph_c) * 100, 1) if len(ph_c) else 0.0
        ph_b = df26['ph_label'].dropna()
        b_prod_pos   = round(ph_b.isin(['Leichte Verbesserung', 'Deutliche Verbesserung']).sum() / len(ph_b) * 100, 1)

        p_c  = df_c['p_label'].dropna()
        kpi_in_prod  = round(p_c.isin(['Phase 3', 'Phase 4']).sum() / len(p_c) * 100, 1) if len(p_c) else 0.0
        p_b  = df26['p_label'].dropna()
        b_in_prod    = round(p_b.isin(['Phase 3', 'Phase 4']).sum() / len(p_b) * 100, 1)

        s_c  = df_c['s_label'].dropna()
        kpi_strat    = round((s_c != 'Bisher weder noch').sum() / len(s_c) * 100, 1) if len(s_c) else 0.0
        s_b  = df26['s_label'].dropna()
        b_strat      = round((s_b != 'Bisher weder noch').sum() / len(s_b) * 100, 1)

        kpis_raw = [
            ('adoption',              kpi_adopt,    b_adopt),
            ('daily_usage',           kpi_daily,    b_daily),
            ('productivity_positive', kpi_prod_pos, b_prod_pos),
            ('in_production',         kpi_in_prod,  b_in_prod),
            ('strategic_lever',       kpi_strat,    b_strat),
        ]
        kpis: list[dict] = []
        for kname, cv, bv in kpis_raw:
            delta = round(cv - bv, 1)
            marker = '  ⚠ IMPLAUSIBLE (>50 pp)' if abs(delta) > 50 else ''
            print(f"    {kname:<25}  company={cv:.1f}%  bench={bv:.1f}%  Δ={delta:+.1f}pp{marker}")
            kpis.append({'key': kname, 'company_value': cv, 'bench_value': bv, 'delta': delta})
        if is_bcg:
            print("    — BCG KPI discrepancy check vs vergleich.html:")
            for kname, cv, _ in kpis_raw:
                _chk(kname, cv, _BCG_REFS['kpis'].get(kname))

        # ── usage_frequency ───────────────────────────────────────────────
        print("\n  usage_frequency:")
        freq_vc_c = df_c['frequenz'].value_counts()
        freq_vc_b = df26['frequenz'].value_counts()
        FREQ_CATS = ['Täglich', 'Wöchentlich', 'Selten', 'Gar nicht']
        usage_freq: list[dict] = []
        for cat in FREQ_CATS:
            cc = int(freq_vc_c.get(cat, 0))
            if cc == 0:
                cc = sum(v for k, v in freq_vc_c.items() if cat.lower() in str(k).lower())
            cv = round(cc / N_C * 100, 1)
            bc = int(freq_vc_b.get(cat, 0))
            if bc == 0:
                bc = sum(v for k, v in freq_vc_b.items() if cat.lower() in str(k).lower())
            bv = round(bc / N * 100, 1)
            print(f"    {cat:<14}  company={cv:.1f}%  bench={bv:.1f}%")
            usage_freq.append({'label': cat, 'company_value': cv, 'bench_value': bv})
        if is_bcg:
            print("    — discrepancy check:")
            for item in usage_freq:
                _chk(item['label'], item['company_value'], _BCG_REFS['usage_frequency'].get(item['label']))

        # ── tools (multi-select) ──────────────────────────────────────────
        print("\n  tools (multi-select):")
        tools_c = df_c['tools'].dropna()
        n_c_tools = len(tools_c)
        comp_tools: list[dict] = []
        for frag, display in _TOOLS_DEF:
            cc = int(tools_c.str.contains(frag, case=False, na=False).sum())
            cv = round(cc / n_c_tools * 100, 1) if n_c_tools else 0.0
            bv = bench_tools_vals[display]
            print(f"    {display:<25}  company={cv:.1f}%  bench={bv:.1f}%  (n_c={n_c_tools}, n_b={n_bench_tools})")
            comp_tools.append({'label': display, 'company_value': cv, 'bench_value': bv})
        if is_bcg:
            print("    — discrepancy check:")
            for item in comp_tools:
                _chk(item['label'], item['company_value'], _BCG_REFS['tools'].get(item['label']))

        # ── productivity (3 bars, merged) ─────────────────────────────────
        print("\n  productivity (3 bars):")
        comp_prod_today  = _prod3(df_c['ph_label'])
        comp_prod_future = _prod3(df_c['pf_label'])
        for ct in comp_prod_today:
            bt = next(x for x in bench_prod_today  if x['label'] == ct['label'])
            print(f"    today   {ct['label']:<32}  company={ct['value']:.1f}%  bench={bt['value']:.1f}%")
        for cf in comp_prod_future:
            bf = next(x for x in bench_prod_future if x['label'] == cf['label'])
            print(f"    future  {cf['label']:<32}  company={cf['value']:.1f}%  bench={bf['value']:.1f}%")
        if is_bcg:
            print("    — discrepancy check today:")
            for i, ct in enumerate(comp_prod_today):
                _chk(ct['label'], ct['value'], _BCG_REFS['prod_today'][i] if i < len(_BCG_REFS['prod_today']) else None)
            print("    — discrepancy check future:")
            for i, cf in enumerate(comp_prod_future):
                _chk(cf['label'], cf['value'], _BCG_REFS['prod_future'][i] if i < len(_BCG_REFS['prod_future']) else None)

        # ── privacy ───────────────────────────────────────────────────────
        print("\n  privacy:")
        DS_FRAGS = [
            ('konsequent auf deren',    'Regelungen bekannt & konsequent'),
            ('besten Gewissens',        'Best-effort Umsetzung'),
            ('nicht immer konsequent',  'Richtlinien bekannt, nicht immer'),
            ('keine konkreten Regeln',  'Keine Regeln bekannt'),
        ]
        ds_vc_c = df_c['datenschutz'].value_counts()
        n_ds_c  = int(ds_vc_c.sum())
        ds_vc_b = df26['datenschutz'].value_counts()
        n_ds_b  = int(ds_vc_b.sum())
        privacy: list[dict] = []
        for frag, display in DS_FRAGS:
            cat_c = next((k for k in ds_vc_c.index if frag.lower() in str(k).lower()), None)
            cv = round(int(ds_vc_c.get(cat_c, 0)) / n_ds_c * 100, 1) if (cat_c and n_ds_c) else 0.0
            cat_b = next((k for k in ds_vc_b.index if frag.lower() in str(k).lower()), None)
            bv = round(int(ds_vc_b.get(cat_b, 0)) / n_ds_b * 100, 1) if (cat_b and n_ds_b) else 0.0
            print(f"    {display:<40}  company={cv:.1f}%  bench={bv:.1f}%")
            privacy.append({'label': display, 'company_value': cv, 'bench_value': bv})
        if is_bcg:
            print("    — discrepancy check:")
            for i, item in enumerate(privacy):
                _chk(item['label'], item['company_value'], _BCG_REFS['privacy'][i] if i < len(_BCG_REFS['privacy']) else None)

        # ── phase_grid ────────────────────────────────────────────────────
        print("\n  phase_grid:")
        p_vc_c = df_c['p_label'].value_counts()
        n_p_c  = int(p_vc_c.sum())
        p_vc_b = df26['p_label'].value_counts()
        n_p_b  = int(p_vc_b.sum())
        phase_grid: list[dict] = []
        for i, ph in enumerate(PHASE_ORDER):
            cv = round(int(p_vc_c.get(ph, 0)) / n_p_c * 100, 1) if n_p_c else 0.0
            bv = round(int(p_vc_b.get(ph, 0)) / n_p_b * 100, 1) if n_p_b else 0.0
            marker = ''
            if is_bcg:
                ref = _BCG_REFS['phase'][i]
                diff = abs(cv - ref)
                marker = f'  ⚠  |Δ|={diff:.1f}pp (ref={ref})' if diff > 0.5 else ''
            print(f"    {ph}  company={cv:.1f}%  bench={bv:.1f}%{marker}")
            phase_grid.append({'phase': ph, 'company_value': cv, 'bench_value': bv})

        # ── challenges_rank ───────────────────────────────────────────────
        print("\n  challenges_rank:")
        chal_vc_c = df_c['herausforderung'].value_counts()
        n_chal_c  = int(chal_vc_c.sum())
        comp_challenges: list[dict] = []
        for cat_key, full_label in _CHAL_CATS.items():
            cc = int(chal_vc_c.get(full_label, 0))
            if cc == 0:
                cc = sum(v for k, v in chal_vc_c.items()
                         if full_label[:20].lower() in str(k).lower())
            cv = round(cc / n_chal_c * 100, 1) if n_chal_c else 0.0
            comp_challenges.append({'cat': cat_key, 'label': _CHAL_SHORT[cat_key], 'value': cv})
        comp_challenges_ranked = sorted(comp_challenges, key=lambda x: -x['value'])
        for i, item in enumerate(comp_challenges_ranked):
            ref_check = ''
            if is_bcg:
                ref = _BCG_REFS['challenges'].get(item['cat'])
                if ref is not None:
                    diff = abs(item['value'] - ref)
                    ref_check = f'  ⚠  |Δ|={diff:.1f}pp (ref={ref})' if diff > 0.5 else f'  ✓ (ref={ref})'
            print(f"    {i+1}. {item['cat']:<7}  {item['label']:<30}  {item['value']:.1f}%{ref_check}")

        # ── proficiency ───────────────────────────────────────────────────
        print("\n  proficiency:")
        k_vc_c = df_c['k_label'].value_counts()
        n_k_c  = int(k_vc_c.sum())
        k_vc_b = df26['k_label'].value_counts()
        n_k_b  = int(k_vc_b.sum())
        proficiency: list[dict] = []
        for i, lev in enumerate(KOMP_ORDER):
            cv = round(int(k_vc_c.get(lev, 0)) / n_k_c * 100, 1) if n_k_c else 0.0
            bv = round(int(k_vc_b.get(lev, 0)) / n_k_b * 100, 1) if n_k_b else 0.0
            marker = ''
            if is_bcg:
                ref = _BCG_REFS['proficiency'][i]
                diff = abs(cv - ref)
                marker = f'  ⚠  |Δ|={diff:.1f}pp (ref={ref})' if diff > 0.5 else ''
            print(f"    {lev:<25}  company={cv:.1f}%  bench={bv:.1f}%{marker}")
            proficiency.append({'level': lev, 'company_value': cv, 'bench_value': bv})

        # ── growth_efficiency (bar chart only — cmp-rows derived at render time) ─
        print("\n  growth_efficiency:")
        s_vc_c = df_c['s_label'].value_counts()
        n_s_c  = int(s_vc_c.sum())
        s_vc_b = df26['s_label'].value_counts()
        n_s_b  = int(s_vc_b.sum())
        growth_eff: list[dict] = []
        for cat in STRAT_ORDER:
            cv = round(int(s_vc_c.get(cat, 0)) / n_s_c * 100, 1) if n_s_c else 0.0
            bv = round(int(s_vc_b.get(cat, 0)) / n_s_b * 100, 1) if n_s_b else 0.0
            marker = ''
            if is_bcg:
                ref = _BCG_REFS['growth_eff'].get(cat)
                if ref is not None:
                    diff = abs(cv - ref)
                    marker = f'  ⚠  |Δ|={diff:.1f}pp (ref={ref})' if diff > 0.5 else ''
            print(f"    {cat:<30}  company={cv:.1f}%  bench={bv:.1f}%{marker}")
            growth_eff.append({'label': cat, 'company_value': cv, 'bench_value': bv})

        # ── productivity_timeline ─────────────────────────────────────────
        has_long = comp['has_longitudinal']
        file24   = comp.get('file24')
        col24    = comp.get('col24_prod')

        if has_long and file24 and (SRC / file24).exists():
            print(f"\n  productivity_timeline (longitudinal)  file24={file24}")

            if col24 is None:
                # Print headers to detect the productivity column
                df24_hdr = pd.read_excel(SRC / file24, sheet_name=0, engine='openpyxl',
                                         header=0, nrows=0)
                print(f"  {file24} column headers:")
                for i, c in enumerate(df24_hdr.columns):
                    print(f"    col {i:>2}: {c}")
                col24 = next(
                    (i for i, c in enumerate(df24_hdr.columns)
                     if any(kw in str(c).lower()
                            for kw in ['produktiv', 'improvement', 'verbesserung'])),
                    None,
                )
                if col24 is None:
                    print(f"  ⚠ Could not auto-detect productivity column — skipping longitudinal")
                    has_long = False

            if has_long and col24 is not None:
                df24_c = pd.read_excel(SRC / file24, sheet_name=0, engine='openpyxl',
                                       usecols=[col24], header=0)
                df24_c.columns = ['prod']
                df24_c['prod_label'] = df24_c['prod'].map(_map_prod)
                n24v = int(df24_c['prod_label'].notna().sum())
                print(f"  2024 data: {n24v} valid responses / {len(df24_c)} rows")

                def _d4(series: pd.Series) -> dict:
                    s = series.dropna(); n = len(s)
                    return {cat: round((s == cat).sum() / n * 100, 1) if n else 0.0
                            for cat in PROD_ORDER}

                p24c  = _merge3_dict(_d4(df24_c['prod_label']))
                p26hc = _merge3_dict(_d4(df_c['ph_label']))
                p26fc = _merge3_dict(_d4(df_c['pf_label']))

                print(f"  {'Category':<32}  {'2024/25':>8}  {'2026h':>7}  {'2026f':>7}")
                for cat3 in PROD_ORDER_3:
                    print(f"  {cat3:<32}  {p24c[cat3]:>8.1f}  {p26hc[cat3]:>7.1f}  {p26fc[cat3]:>7.1f}")

                tl_datasets = [
                    {'label': cat3,
                     'values': [p24c[cat3], p26hc[cat3], p26fc[cat3]]}
                    for cat3 in PROD_ORDER_3
                ]
                if is_bcg:
                    print("    — BCG timeline discrepancy check:")
                    for ds in tl_datasets:
                        ref_vals = _BCG_REFS['timeline'].get(ds['label'], [])
                        for idx, (v, ref) in enumerate(zip(ds['values'], ref_vals)):
                            _chk(f"{ds['label'][:20]}[{idx}]", v, ref)

                productivity_timeline: dict = {
                    'labels': ['2024\u2009/\u200925',
                               '2026\u2009(heute)',
                               '2026\u2009(in\u00a01\u20133\u00a0J.)'],
                    'forecast_from_index': 1,
                    'datasets': tl_datasets,
                }
        elif not has_long:
            # K&N: 2-point (heute + in 1-3 J. only)
            print("\n  productivity_timeline (2-point, no 2024 data):")

            def _d4_2(series: pd.Series) -> dict:
                s = series.dropna(); n = len(s)
                return {cat: round((s == cat).sum() / n * 100, 1) if n else 0.0
                        for cat in PROD_ORDER}

            p26hc = _merge3_dict(_d4_2(df_c['ph_label']))
            p26fc = _merge3_dict(_d4_2(df_c['pf_label']))

            tl_datasets = [
                {'label': cat3, 'values': [p26hc[cat3], p26fc[cat3]]}
                for cat3 in PROD_ORDER_3
            ]
            for ds in tl_datasets:
                print(f"    {ds['label']:<32}  heute={ds['values'][0]:.1f}%  future={ds['values'][1]:.1f}%")

            productivity_timeline = {
                'labels': ['2026\u2009(heute)', '2026\u2009(in\u00a01\u20133\u00a0J.)'],
                'forecast_from_index': 0,
                'datasets': tl_datasets,
            }
        else:
            # Longitudinal requested but file missing (Regiocom24 not yet available)
            print(f"\n  ⚠ {file24} not found — productivity_timeline omitted")
            productivity_timeline = {}

        result[ckey] = {
            'meta': {
                'has_longitudinal':   has_long,
                'n_company':          N_C,
                'n_benchmark':        N,
                'n_benchmark_users':  n_bench_tools,
                'display':            comp['display'],
                'industry_i18n':      comp['industry_i18n'],
            },
            'kpis': kpis,
            'sections': {
                'usage_frequency': usage_freq,
                'tools': {
                    'items':            comp_tools,
                    'n_bench_override': n_bench_tools,
                },
                'productivity': {
                    'today':  {'items': comp_prod_today,  'bench': bench_prod_today},
                    'future': {'items': comp_prod_future, 'bench': bench_prod_future},
                },
                'privacy':          privacy,
                'phase_grid':       phase_grid,
                'challenges_rank':  {
                    'benchmark': bench_challenges_ranked,
                    'company':   comp_challenges_ranked,
                },
                'proficiency':      proficiency,
                'growth_efficiency': growth_eff,
            },
            'charts': {
                'productivity_timeline': productivity_timeline,
            },
            # NOTE: fazit text is authored manually in data/data.json and is not generated from Excel.
            # Placeholders are set here and then replaced from existing data.json before writing output.
            'fazit': {'de': '', 'en': ''},
        }

    return result


# ═════════════════════════════════════════════════════════════════════════════
#  Assemble and write
# ═════════════════════════════════════════════════════════════════════════════

output = {
    'report': {
        'meta': {
            'n_total': N,
            'year': 2026,
            'sources': ['general26', 'BCG26', 'Regiocom26', 'KühneUndNagel26'],
        },
        'charts': {
            'challenges_by_stage':   build_challenges_by_stage(),
            'stacked_proficiency':   build_stacked_proficiency(),
            'growth_by_phase':       build_growth_by_phase(),
            'growth_by_proficiency': build_growth_by_proficiency(),
            'productivity_timeline': build_productivity_timeline(),
        },
        'components': build_components(),
    },
    'comparative': build_comparative(),
}

# Preserve manually authored company summaries across pipeline runs.
# These texts are editorial interpretation and must not be generated from survey tables.
if OUT.exists():
    try:
        with open(OUT, 'r', encoding='utf-8') as f:
            prev = json.load(f)
        prev_cmp = prev.get('comparative', {}) if isinstance(prev, dict) else {}
        for key, cmp in output.get('comparative', {}).items():
            prev_fazit = prev_cmp.get(key, {}).get('fazit', {}) if isinstance(prev_cmp, dict) else {}
            if isinstance(prev_fazit, dict):
                cmp['fazit'] = {
                    'de': prev_fazit.get('de', cmp['fazit'].get('de', '')),
                    'en': prev_fazit.get('en', cmp['fazit'].get('en', '')),
                }
    except Exception as exc:
        print(f"⚠ Could not preserve manual fazit text from existing data.json: {exc}")

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print("=" * 70)
print(f"Written:  {OUT}")
print(f"Size:     {OUT.stat().st_size:,} bytes")
print()
print("i18n keys not yet in i18n.js — add these translations:")
print("  results2026.findings.productivity.none_neg  (merged Negativ+Keine, replaces .none and .negative)")
print("  results2026.privacy.konsequent / bestEffort / notAlways / noRules")
print("  growthEfficiency.cat.efficiency / both / growth / neither")
print("  cmp.meta.industry.consulting / it_services / logistics")
print("  cmp.kpi.adoption / daily_usage / productivity_positive / in_production / strategic_lever")
print("=" * 70)
