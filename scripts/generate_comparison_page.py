"""
Automatic Company Comparison HTML Generator
============================================

This script generates a complete vergleich.html (company comparison page) 
automatically from company-specific survey data.

Usage:
    python generate_comparison_page.py data/comp1.xlsx "BCG" "IT-Consulting"
    
Arguments:
    1. Path to company data file (Excel or CSV)
    2. Company name (e.g., "BCG", "Accenture")
    3. Industry category (e.g., "IT-Consulting", "Entwicklung & Architektur")
    
Output:
    - Generated HTML file: vergleich_{company}.html
    - JSON file with all metrics: comparison_{company}.json
"""

import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# ============================================================================
# CONFIGURATION
# ============================================================================

OVERALL_DATA_PATH = Path("data/results.CSV")
DELIMITER = ";"

# Column mappings (German survey questions)
COLUMNS = {
    'work_area': 'In welchem Bereich arbeitest du hauptsächlich?',
    'company_size': 'Wie groß ist dein Unternehmen?',
    'industry': 'In welcher Branche ist dein Unternehmen tätig?',
    'usage_frequency': 'Wie häufig nutzt du GenAI-Tools im beruflichen Umfeld?',
    'tasks': 'Für welche Aufgaben setzt du GenAI hauptsächlich ein?',
    'tools': 'Welche GenAI Modelle/Tools nutzt du?',
    'competence': 'Wie schätzt du aktuell deine Kompetenz im Umgang mit GenAI ein?',
    'productivity_today': 'Heute',
    'productivity_future': 'In 1-3 Jahren',
    'confidence': 'Wie sicher fühlst du dich bei der Einordnung der Ergebnisse von GenAI-Antworten?',
    'non_usage_reason': 'Warum nutzt du keine GenAI-Tools?',
    'improvements': 'In welchen Bereichen wünschst du dir Verbesserungen bei der persönlichen Nutzung von GenAI-Tools?',
    'privacy_awareness': 'Bist du dir der Datenschutz-/Datensicherheitsregeln bezüglich der Nutzung von GenAI-Tools bewusst?',
    'strategic_impact': 'GenAI wird aktuell als Wachstumstreiber und als Effizienzhebel beschrieben. Wie denkst du wird sich GenAI primär in deinem Unternehmen auswirken?',
    'implementation_stage': 'In welchem Stadium befinden sich die Dir bekannten KI-Anwendungsfälle überwiegend',
    'challenges': 'Was ist aktuell die größte Herausforderung beim unternehmensweiten Einsatz von (Gen)AI?',
    'model_strategy': 'Welche Modellstrategie wird Deiner Einschätzung nach in den nächsten 5 Jahren dominieren?'
}


# ============================================================================
# DATA LOADING
# ============================================================================

def load_data(file_path: str) -> pd.DataFrame:
    """Load data from Excel or CSV file."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    if path.suffix.lower() in ['.xlsx', '.xls']:
        return pd.read_excel(path)
    elif path.suffix.lower() == '.csv':
        return pd.read_csv(path, delimiter=DELIMITER)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")


# ============================================================================
# METRIC CALCULATIONS
# ============================================================================

def calculate_percentage(df: pd.DataFrame, column: str, value: str) -> float:
    """Calculate percentage of responses matching a value."""
    total = len(df)
    if total == 0:
        return 0.0
    matches = df[column].str.contains(value, case=False, na=False).sum()
    return round((matches / total) * 100, 1)


def calculate_usage_frequency(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate usage frequency distribution."""
    col = COLUMNS['usage_frequency']
    total = len(df)
    
    if col not in df.columns or total == 0:
        return {'Täglich': 0, 'Wöchentlich': 0, 'Selten': 0, 'Gar nicht': 0}
    
    counts = df[col].value_counts()
    
    return {
        'Täglich': round((counts.get('Täglich', 0) / total) * 100, 1),
        'Wöchentlich': round((counts.get('Wöchentlich', 0) / total) * 100, 1),
        'Selten': round((counts.get('Selten', 0) / total) * 100, 1),
        'Gar nicht': round((counts.get('Gar nicht', 0) / total) * 100, 1)
    }


def calculate_tool_usage(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate tool usage percentages (multi-select)."""
    col = COLUMNS['tools']
    total = len(df[df[col].notna()])  # Only users who answered
    
    if total == 0:
        return {}
    
    tools = {
        'ChatGPT': 'ChatGPT',
        'Microsoft Copilot': 'Copilot',
        'Google Gemini': 'Gemini',
        'Anthropic Claude': 'Claude',
        'Local/Open Source': 'Open Source',
    }
    
    results = {}
    for tool_name, search_term in tools.items():
        matches = df[col].str.contains(search_term, case=False, na=False).sum()
        results[tool_name] = round((matches / total) * 100, 1)
    
    return results


def calculate_productivity_metrics(df: pd.DataFrame, time_col: str) -> Dict[str, float]:
    """Calculate productivity perception metrics."""
    total = len(df[df[time_col].notna()])
    
    if total == 0:
        return {
            'significant': 0,
            'slight': 0,
            'none': 0,
            'negative': 0,
            'total_positive': 0
        }
    
    col_data = df[time_col].fillna('')
    
    # Map German responses to categories
    significant = col_data.str.contains('Deutlich', case=False).sum()
    slight = col_data.str.contains('Leicht', case=False).sum()
    none = col_data.str.contains('Keine', case=False).sum()
    negative = col_data.str.contains('Verschlechterung', case=False).sum()
    
    return {
        'significant': round((significant / total) * 100, 1),
        'slight': round((slight / total) * 100, 1),
        'none': round((none / total) * 100, 1),
        'negative': round((negative / total) * 100, 1),
        'total_positive': round(((significant + slight) / total) * 100, 1)
    }


def calculate_implementation_phases(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate distribution across implementation phases."""
    col = COLUMNS['implementation_stage']
    total = len(df[df[col].notna()])
    
    if total == 0:
        return {}
    
    phases = {
        'phase1': 'Konzeption',
        'phase2': 'Prototyp',
        'phase3': 'Produktiv',
        'phase4': 'Rollout'
    }
    
    results = {}
    for phase_key, search_term in phases.items():
        matches = df[col].str.contains(search_term, case=False, na=False).sum()
        results[phase_key] = round((matches / total) * 100, 1)
    
    # Calculate combined advanced phases
    results['phase34_combined'] = results.get('phase3', 0) + results.get('phase4', 0)
    
    return results


def calculate_top_challenges(df: pd.DataFrame, top_n: int = 5) -> List[Dict]:
    """Get top N challenges with percentages."""
    col = COLUMNS['challenges']
    total = len(df[df[col].notna()])
    
    if total == 0:
        return []
    
    counts = df[col].value_counts().head(top_n)
    
    results = []
    for rank, (challenge, count) in enumerate(counts.items(), 1):
        percentage = round((count / total) * 100, 1)
        results.append({
            'rank': rank,
            'challenge': challenge,
            'count': count,
            'percentage': percentage
        })
    
    return results


def calculate_comparison_metrics(company_df: pd.DataFrame, overall_df: pd.DataFrame) -> Dict:
    """Calculate all comparison metrics between company and overall data."""
    
    # Sample sizes
    company_n = len(company_df)
    overall_n = len(overall_df)
    
    # Usage frequency
    company_usage = calculate_usage_frequency(company_df)
    overall_usage = calculate_usage_frequency(overall_df)
    
    usage_comparison = {}
    for freq in ['Täglich', 'Wöchentlich', 'Selten', 'Gar nicht']:
        company_val = company_usage.get(freq, 0)
        overall_val = overall_usage.get(freq, 0)
        usage_comparison[freq] = {
            'company': company_val,
            'overall': overall_val,
            'delta': round(company_val - overall_val, 1)
        }
    
    # Tool usage
    company_tools = calculate_tool_usage(company_df)
    overall_tools = calculate_tool_usage(overall_df)
    
    tools_comparison = {}
    for tool in company_tools.keys():
        company_val = company_tools.get(tool, 0)
        overall_val = overall_tools.get(tool, 0)
        tools_comparison[tool] = {
            'company': company_val,
            'overall': overall_val,
            'delta': round(company_val - overall_val, 1)
        }
    
    # Productivity today
    company_prod_today = calculate_productivity_metrics(company_df, COLUMNS['productivity_today'])
    overall_prod_today = calculate_productivity_metrics(overall_df, COLUMNS['productivity_today'])
    
    # Productivity future
    company_prod_future = calculate_productivity_metrics(company_df, COLUMNS['productivity_future'])
    overall_prod_future = calculate_productivity_metrics(overall_df, COLUMNS['productivity_future'])
    
    # Implementation phases
    company_phases = calculate_implementation_phases(company_df)
    overall_phases = calculate_implementation_phases(overall_df)
    
    phases_comparison = {}
    for phase in ['phase1', 'phase2', 'phase3', 'phase4', 'phase34_combined']:
        company_val = company_phases.get(phase, 0)
        overall_val = overall_phases.get(phase, 0)
        phases_comparison[phase] = {
            'company': company_val,
            'overall': overall_val,
            'delta': round(company_val - overall_val, 1)
        }
    
    # Top challenges
    company_challenges = calculate_top_challenges(company_df)
    overall_challenges = calculate_top_challenges(overall_df)
    
    return {
        'sample_sizes': {
            'company': company_n,
            'overall': overall_n
        },
        'usage_frequency': usage_comparison,
        'tool_usage': tools_comparison,
        'productivity_today': {
            'company': company_prod_today,
            'overall': overall_prod_today
        },
        'productivity_future': {
            'company': company_prod_future,
            'overall': overall_prod_future
        },
        'implementation_phases': phases_comparison,
        'challenges': {
            'company': company_challenges,
            'overall': overall_challenges
        }
    }


# ============================================================================
# HTML GENERATION
# ============================================================================

def generate_comparison_bar_html(label: str, overall_val: float, company_val: float, 
                                 delta: float, overall_label: str = "Alle", 
                                 company_label: str = "Unternehmen") -> str:
    """Generate HTML for a single comparison bar."""
    
    # Determine delta styling
    if delta > 0:
        delta_class = "cmp-delta--pos"
        delta_symbol = "+&thinsp;"
    elif delta < 0:
        delta_class = "cmp-delta--neg"
        delta_symbol = "−&thinsp;"
    else:
        delta_class = "cmp-delta--neu"
        delta_symbol = "±&thinsp;"
    
    delta_abs = abs(delta)
    
    html = f"""
                    <div class="cmp-row">
                        <div class="cmp-row__header">
                            <span class="cmp-row__label">{label}</span>
                            <span class="cmp-delta {delta_class}">{delta_symbol}{delta_abs:,.1f}&thinsp;PP</span>
                        </div>
                        <div class="cmp-bars">
                            <div class="cmp-bar-row">
                                <span class="cmp-bar-row__who">{overall_label}</span>
                                <div class="cmp-bar-row__track"><div class="cmp-bar-row__fill fill--bench" style="width:{overall_val}%;"></div></div>
                                <span class="cmp-bar-row__val" style="color:#1565C0;">{overall_val:,.1f}&thinsp;%</span>
                            </div>
                            <div class="cmp-bar-row">
                                <span class="cmp-bar-row__who" style="font-weight:600;color:var(--th-blue);">{company_label}</span>
                                <div class="cmp-bar-row__track"><div class="cmp-bar-row__fill fill--company" style="width:{company_val}%;"></div></div>
                                <span class="cmp-bar-row__val" style="color:#004A99;">{company_val:,.1f}&thinsp;%</span>
                            </div>
                        </div>
                    </div>
"""
    return html


def generate_kpi_card_html(title: str, company_val: float, overall_val: float, 
                           delta: float, unit: str = "%") -> str:
    """Generate HTML for a KPI card."""
    
    if delta > 0:
        delta_class = "cmp-delta--pos"
        delta_symbol = "+"
    elif delta < 0:
        delta_class = "cmp-delta--neg"
        delta_symbol = "−"
    else:
        delta_class = "cmp-delta--neu"
        delta_symbol = "±"
    
    delta_abs = abs(delta)
    
    html = f"""
            <div class="kpi-card">
                <div class="kpi-card__title">{title}</div>
                <div class="kpi-card__value" style="color:#004A99;">{company_val:,.1f}<span>{unit}</span></div>
                <div class="kpi-card__sub">Unternehmen</div>
                <div class="kpi-card__bench">Gesamt: {overall_val:,.1f}{unit}</div>
                <div class="kpi-card__delta {delta_class}">{delta_symbol}&thinsp;{delta_abs:,.1f}&thinsp;PP</div>
            </div>
"""
    return html


def generate_complete_html(company_name: str, industry: str, metrics: Dict, 
                          output_path: str = None) -> str:
    """Generate complete vergleich.html page."""
    
    company_n = metrics['sample_sizes']['company']
    overall_n = metrics['sample_sizes']['overall']
    
    # Generate usage frequency bars
    usage_bars = ""
    for freq in ['Täglich', 'Wöchentlich', 'Selten', 'Gar nicht']:
        data = metrics['usage_frequency'][freq]
        usage_bars += generate_comparison_bar_html(
            freq, data['overall'], data['company'], data['delta'],
            f"Alle (n={overall_n})", company_name
        )
    
    # Generate tool usage bars
    tool_bars = ""
    tool_names = {
        'ChatGPT': 'OpenAI ChatGPT',
        'Microsoft Copilot': 'Microsoft Copilot',
        'Google Gemini': 'Google Gemini',
        'Anthropic Claude': 'Anthropic Claude'
    }
    for tool_key, tool_display in tool_names.items():
        if tool_key in metrics['tool_usage']:
            data = metrics['tool_usage'][tool_key]
            tool_bars += generate_comparison_bar_html(
                tool_display, data['overall'], data['company'], data['delta'],
                f"Alle (n={overall_n})", company_name
            )
    
    # Generate productivity today bars
    prod_today_bars = ""
    prod_labels = {
        'significant': 'Deutliche Verbesserung',
        'slight': 'Leichte Verbesserung',
        'none': 'Keine / Negative Änderung'
    }
    for key, label in prod_labels.items():
        company_val = metrics['productivity_today']['company'][key]
        overall_val = metrics['productivity_today']['overall'][key]
        delta = round(company_val - overall_val, 1)
        prod_today_bars += generate_comparison_bar_html(
            label, overall_val, company_val, delta, "Alle", company_name
        )
    
    # Generate productivity future bars
    prod_future_bars = ""
    for key, label in prod_labels.items():
        company_val = metrics['productivity_future']['company'][key]
        overall_val = metrics['productivity_future']['overall'][key]
        delta = round(company_val - overall_val, 1)
        prod_future_bars += generate_comparison_bar_html(
            label, overall_val, company_val, delta, "Alle", company_name
        )
    
    # Generate KPI cards
    kpi_daily_usage = generate_kpi_card_html(
        "Tägliche Nutzung",
        metrics['usage_frequency']['Täglich']['company'],
        metrics['usage_frequency']['Täglich']['overall'],
        metrics['usage_frequency']['Täglich']['delta']
    )
    
    kpi_productivity = generate_kpi_card_html(
        "sehen eine Produktivitätssteigerung",
        metrics['productivity_today']['company']['total_positive'],
        metrics['productivity_today']['overall']['total_positive'],
        metrics['productivity_today']['company']['total_positive'] - metrics['productivity_today']['overall']['total_positive']
    )
    
    kpi_advanced_phases = generate_kpi_card_html(
        "Im Produktiveinsatz (Phase 3+4)",
        metrics['implementation_phases']['phase34_combined']['company'],
        metrics['implementation_phases']['phase34_combined']['overall'],
        metrics['implementation_phases']['phase34_combined']['delta']
    )
    
    # Read template and inject data
    # For now, return a simplified version showing key metrics
    
    html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Unternehmensvergleich {company_name} | KI im IT-Arbeitsalltag</title>
    <link href="styles.css" rel="stylesheet">
</head>
<body>
<main>
<section class="hero">
    <div class="container">
        <h1>Unternehmensvergleich {company_name} 2026</h1>
        <p>Direkter Vergleich der {company_name} (n={company_n}) mit dem Gesamtdurchschnitt der 2026-Studie (n={overall_n}). <br>Branche: {industry}</p>
    </div>
</section>

<section class="section">
    <div class="container">
        <h2>Kernzahlen</h2>
        <div class="grid grid--3" style="gap:1.5rem;">
            {kpi_daily_usage}
            {kpi_productivity}
            {kpi_advanced_phases}
        </div>
    </div>
</section>

<section class="section section--alt">
    <div class="container">
        <h2>Nutzungshäufigkeit</h2>
        <div class="card">
            <div class="card__body">
{usage_bars}
            </div>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <h2>Genutzte GenAI-Tools</h2>
        <div class="card">
            <div class="card__body">
{tool_bars}
            </div>
        </div>
    </div>
</section>

<section class="section section--alt">
    <div class="container">
        <h2>Produktivität heute</h2>
        <div class="card">
            <div class="card__body">
{prod_today_bars}
            </div>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <h2>Produktivität in 1-3 Jahren</h2>
        <div class="card">
            <div class="card__body">
{prod_future_bars}
            </div>
        </div>
    </div>
</section>

</main>
</body>
</html>"""
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML generated: {output_path}")
    
    return html_content


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    
    if len(sys.argv) < 4:
        print("Usage: python generate_comparison_page.py <company_data_file> <company_name> <industry>")
        print("Example: python generate_comparison_page.py data/comp1.xlsx 'BCG' 'IT-Consulting'")
        sys.exit(1)
    
    company_data_file = sys.argv[1]
    company_name = sys.argv[2]
    industry = sys.argv[3]
    
    print("=" * 80)
    print(f"GENERATING COMPARISON PAGE FOR {company_name.upper()}")
    print("=" * 80)
    
    # Load data
    print("\n📂 Loading data...")
    company_df = load_data(company_data_file)
    overall_df = load_data(OVERALL_DATA_PATH)
    
    print(f"  • Company data: {len(company_df)} respondents")
    print(f"  • Overall data: {len(overall_df)} respondents")
    
    # Calculate metrics
    print("\n📊 Calculating comparison metrics...")
    metrics = calculate_comparison_metrics(company_df, overall_df)
    
    # Export metrics to JSON
    json_output = f"comparison_{company_name.lower().replace(' ', '_')}.json"
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Metrics exported: {json_output}")
    
    # Generate HTML
    print("\n🔨 Generating HTML...")
    html_output = f"vergleich_{company_name.lower().replace(' ', '_')}.html"
    generate_complete_html(company_name, industry, metrics, html_output)
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nCompany: {company_name} (n={metrics['sample_sizes']['company']})")
    print(f"Industry: {industry}")
    print(f"\nKey Metrics vs. Overall (n={metrics['sample_sizes']['overall']}):")
    print(f"  • Daily usage: {metrics['usage_frequency']['Täglich']['company']}% "
          f"(Δ {metrics['usage_frequency']['Täglich']['delta']:+.1f}pp)")
    print(f"  • Total positive productivity: {metrics['productivity_today']['company']['total_positive']}% "
          f"(Δ {metrics['productivity_today']['company']['total_positive'] - metrics['productivity_today']['overall']['total_positive']:+.1f}pp)")
    print(f"  • Advanced phases (3+4): {metrics['implementation_phases']['phase34_combined']['company']}% "
          f"(Δ {metrics['implementation_phases']['phase34_combined']['delta']:+.1f}pp)")
    
    print(f"\n✅ Generation complete!")
    print(f"   HTML: {html_output}")
    print(f"   JSON: {json_output}")
    print("=" * 80)


if __name__ == "__main__":
    main()
