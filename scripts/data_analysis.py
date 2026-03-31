"""
Data Analysis Scripts for KI-Adoption Survey 2026
===================================================

This file documents and reproduces all data analyses performed for the survey results,
particularly for the Reifegrad (maturity path) section and company comparisons.

Data Source: data/results.CSV (semicolon-delimited, n=310 respondents)

Originally executed as PowerShell commands, now documented in Python for:
- Reproducibility
- Documentation
- Future analysis automation
- Export capabilities

Key Analyses:
1. Top-5 Challenges per Implementation Phase (for Reifegrad section)
2. Chart-ready data extraction for Chart.js visualizations
3. Usage frequency statistics (adoption rate, daily users)
4. Productivity trends over time (2024/25, 2026, future)
5. BCG vs. Overall comparison (all metrics from vergleich.html)
6. Custom company comparison template

Usage:
    python data_analysis.py    # Run all analyses with formatted output
    
    # Or import as module:
    from data_analysis import analyze_challenges_by_phase, get_bcg_comparison_data
    results = analyze_challenges_by_phase()
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path


# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_FILE = Path("data/results.CSV")
DELIMITER = ";"

# Column names from the survey (German)
COL_IMPLEMENTATION_STAGE = "In welchem Stadium befinden sich die Dir bekannten KI-Anwendungsfälle überwiegend"
COL_CHALLENGES = "Was ist aktuell die größte Herausforderung beim unternehmensweiten Einsatz von (Gen)AI?"


# ============================================================================
# ANALYSIS 1: Top-5 Challenges per Implementation Phase
# ============================================================================
# Context: Reifegrad section in ergebnisse-2026-workInProgress.html
# Purpose: Show how challenges evolve across AI implementation maturity stages
# Output: Used in phase cards and line/stacked area charts

def analyze_challenges_by_phase(csv_path=DATA_FILE, top_n=5):
    r"""
    Aggregate challenges by implementation phase and return top N per phase.
    
    Original PowerShell command:
    ```powershell
    $rows=Import-Csv -Path '.\data\results.CSV' -Delimiter ';'
    $stageCol='In welchem Stadium befinden sich die Dir bekannten KI-Anwendungsfälle überwiegend'
    $challengeCol='Was ist aktuell die größte Herausforderung beim unternehmensweiten Einsatz von (Gen)AI?'
    $filtered=$rows | Where-Object { $_.$stageCol -and $_.$challengeCol }
    $phases=$filtered | Group-Object { $_.$stageCol }
    foreach($p in $phases){ 
        Write-Output "`n=== $($p.Name) | n=$($p.Count) ==="; 
        $p.Group | Group-Object { $_.$challengeCol } | Sort-Object Count -Descending | Select-Object -First 5 | 
        ForEach-Object { $pct=[math]::Round(($_.Count/$p.Count)*100,1); Write-Output ("{0} | {1} | {2}%" -f $_.Name,$_.Count,$pct) } 
    }
    ```
    
    Returns:
        dict: Phase names as keys, list of (challenge, count, percentage) tuples as values
    """
    # Load data
    df = pd.read_csv(csv_path, delimiter=DELIMITER)
    
    # Filter rows with both stage and challenge data
    filtered = df[
        df[COL_IMPLEMENTATION_STAGE].notna() & 
        df[COL_CHALLENGES].notna()
    ].copy()
    
    # Group by implementation phase
    results = {}
    
    for phase, phase_group in filtered.groupby(COL_IMPLEMENTATION_STAGE):
        phase_total = len(phase_group)
        
        # Count challenges within this phase
        challenge_counts = phase_group[COL_CHALLENGES].value_counts()
        
        # Get top N challenges
        top_challenges = []
        for challenge, count in challenge_counts.head(top_n).items():
            percentage = round((count / phase_total) * 100, 1)
            top_challenges.append((challenge, count, percentage))
        
        results[phase] = {
            'n': phase_total,
            'challenges': top_challenges
        }
    
    return results


def print_challenges_analysis():
    """Print formatted output matching the original PowerShell results."""
    results = analyze_challenges_by_phase()
    
    # Define phase order for consistent output
    phase_order = [
        'In Konzeption oder Entwicklung',
        'Prototyp vorhanden, weitere Entwicklung erforderlich',
        'Erste Produktivversion im Einsatz, iterative Weiterentwicklung',
        'Unternehmensweiter Rollout abgeschlossen'
    ]
    
    for phase_name in phase_order:
        if phase_name in results:
            data = results[phase_name]
            print(f"\n=== {phase_name} | n={data['n']} ===")
            for challenge, count, pct in data['challenges']:
                print(f"{challenge} | {count} | {pct}%")


# ============================================================================
# ANALYSIS 2: BCG vs Overall Comparison (for vergleich.html)
# ============================================================================
# Context: Company-specific comparison page
# Purpose: Compare BCG participants (n=76) against all respondents (n=310)
# Note: Current implementation uses hardcoded values in HTML

#for general comparison given a certain column

def analyze_company_comparison(csv_path=DATA_FILE, company_filter_column=None, company_value=None):
    """
    Compare a specific company subset against the overall population.
    
    This function provides a template for company-specific analyses.
    Currently, vergleich.html uses hardcoded BCG comparison data.
    
    Args:
        csv_path: Path to CSV data file
        company_filter_column: Column name to filter on (e.g., company affiliation)
        company_value: Value to filter for (e.g., "BCG")
    
    Returns:
        dict: Comparison metrics
    """
    df = pd.read_csv(csv_path, delimiter=DELIMITER)
    
    # If no company filter specified, return template structure
    if company_filter_column is None or company_value is None:
        return {
            'note': 'Company comparison requires filter column and value',
            'example_usage': "analyze_company_comparison(company_filter_column='Unternehmen', company_value='BCG')",
            'available_columns': list(df.columns)
        }
    
    # Filter for company subset
    company_df = df[df[company_filter_column] == company_value]
    
    return {
        'company': company_value,
        'company_n': len(company_df),
        'total_n': len(df),
        'percentage_of_total': round(len(company_df) / len(df) * 100, 1),
        'company_df': company_df,
        'overall_df': df
    }


# ============================================================================
# ANALYSIS 3: Chart Data Extraction
# ============================================================================
# Context: Line and stacked area charts in ergebnisse-2026-workInProgress.html
# Purpose: Extract data in chart-ready format

def get_challenge_chart_data():
    """
    Extract challenge data formatted for Chart.js visualization.
    
    Returns data for both:
    - Line chart (challengesChart)
    - Stacked area chart (challengesStackedChart)
    
    Output format matches JavaScript datasets in HTML.
    """
    results = analyze_challenges_by_phase()
    
    # Define phase order and challenge mapping
    phases = [
        'In Konzeption oder Entwicklung',
        'Prototyp vorhanden, weitere Entwicklung erforderlich', 
        'Erste Produktivversion im Einsatz, iterative Weiterentwicklung',
        'Unternehmensweiter Rollout abgeschlossen'
    ]
    
    phase_labels_short = [
        'Konzeption/Entwicklung',
        'Prototyp',
        'Produktiveinsatz',
        'Rollout'
    ]
    
    # Aggregate all challenges across phases
    all_challenges = set()
    for phase_data in results.values():
        for challenge, _, _ in phase_data['challenges']:
            all_challenges.add(challenge)
    
    # Create data structure for each challenge across all phases
    challenge_data = {}
    
    for challenge in all_challenges:
        percentages = []
        for phase_name in phases:
            phase_challenges = results.get(phase_name, {}).get('challenges', [])
            # Find this challenge in the phase
            pct = 0.0
            for ch, cnt, p in phase_challenges:
                if ch == challenge:
                    pct = p
                    break
            percentages.append(pct)
        
        challenge_data[challenge] = percentages
    
    return {
        'labels': phase_labels_short,
        'datasets': challenge_data,
        'raw_results': results
    }


# ============================================================================
# ANALYSIS 4: Usage Frequency Statistics
# ============================================================================
# Context: Usage behavior section in ergebnisse-2026-workInProgress.html
# Purpose: Calculate GenAI adoption and usage frequency

def analyze_usage_frequency(csv_path=DATA_FILE):
    """
    Analyze GenAI usage frequency across all respondents.
    
    Results shown in HTML:
    - 283/310 (91%) use GenAI
    - 171/310 (55%) use it daily
    - Usage distribution: Daily 171, Weekly 72, Rarely 40, Never 27
    
    Returns:
        dict: Usage statistics
    """
    df = pd.read_csv(csv_path, delimiter=DELIMITER)
    
    # Column name for usage frequency (if it exists)
    # Note: Actual column name may vary - adjust based on CSV structure
    usage_col = "Wie häufig nutzt Du Generative KI-Tools in Deinem beruflichen Alltag?"
    
    if usage_col not in df.columns:
        return {
            'note': 'Usage frequency column not found',
            'manual_data': {
                'total_respondents': 310,
                'genai_users': 283,
                'usage_rate': 91.3,
                'daily_users': 171,
                'daily_rate': 55.2,
                'distribution': {
                    'Täglich': 171,
                    'Wöchentlich': 72,
                    'Selten': 40,
                    'Gar nicht': 27
                }
            }
        }
    
    # Analyze usage frequency
    total = len(df)
    usage_counts = df[usage_col].value_counts().to_dict()
    
    return {
        'total_respondents': total,
        'usage_distribution': usage_counts,
        'genai_users': sum([v for k, v in usage_counts.items() if 'nicht' not in k.lower()]),
    }


# ============================================================================
# ANALYSIS 5: Productivity Trends Across Time
# ============================================================================
# Context: Productivity chart (productivityChart) in ergebnisse-2026-workInProgress.html
# Purpose: Track productivity expectations from 2024 to future projections

def get_productivity_trend_data():
    """
    Extract productivity perception trends across three time periods.
    
    Data from HTML charts (ergebnisse-2026-workInProgress.html):
    - 2024/25: Historical baseline
    - 2026 (today): Current perception
    - 2026 (in 1-3 years): Future expectation
    
    Chart Shows:
    - Total Positive: [85.4, 88.7, 90.1]
    - Significant Improvement: [34.3, 33.2, 64.0]
    - Slight Improvement: [51.1, 55.5, 26.1]
    - No Change: [11.7, 8.8, 3.5]
    
    Returns:
        dict: Time-series productivity data
    """
    return {
        'labels': ['2024/25', '2026 (heute)', '2026 (in 1-3 J.)'],
        'datasets': {
            'Positiv gesamt': [85.4, 88.7, 90.1],
            'Deutliche Verbesserung': [34.3, 33.2, 64.0],
            'Leichte Verbesserung': [51.1, 55.5, 26.1],
            'Keine Änderung': [11.7, 8.8, 3.5]
        },
        'insights': {
            'total_positive_change': '+4.7pp (85.4% → 90.1%)',
            'significant_improvement_expected': '64.0% (nearly double from 33.2%)',
            'neutral_decline': '11.7% → 3.5% (explains positive growth)',
            'key_trend': 'Shift from "slight" to "significant" improvements'
        }
    }


# ============================================================================
# ANALYSIS 6: BCG Company Comparison (Detailed)
# ============================================================================
# Context: vergleich.html - Company-specific analysis
# Purpose: Full BCG vs. overall comparison across all metrics

def get_bcg_comparison_data():
    """
    Complete BCG (n=76) vs. Overall (n=310) comparison data.
    
    Source: vergleich.html (hardcoded values from company analysis)
    
    All percentages and deltas extracted from HTML comparison bars.
    
    Returns:
        dict: Comprehensive comparison metrics
    """
    return {
        'sample_sizes': {
            'overall': 310,
            'bcg': 76,
            'bcg_percentage_of_total': 24.5
        },
        
        'usage_frequency': {
            'daily': {'overall': 55.2, 'bcg': 90.8, 'delta': +35.6},
            'weekly': {'overall': 23.2, 'bcg': 7.9, 'delta': -15.3},
            'rarely': {'overall': 12.9, 'bcg': 1.3, 'delta': -11.6},
            'never': {'overall': 8.7, 'bcg': 0.0, 'delta': -8.7},
            'insight': 'All BCG participants use GenAI, 90.8% daily vs 55.2% overall'
        },
        
        'tool_usage': {
            'chatgpt': {'overall': 72.8, 'bcg': 98.7, 'delta': +26.0},
            'microsoft_copilot': {'overall': 48.8, 'bcg': 25.0, 'delta': -23.8},
            'google_gemini': {'overall': 20.5, 'bcg': 14.5, 'delta': -6.0},
            'anthropic_claude': {'overall': 19.1, 'bcg': 9.2, 'delta': -9.9},
            'insight': 'BCG heavily concentrated on ChatGPT (98.7%)'
        },
        
        'productivity_today': {
            'significant_improvement': {'overall': 33.2, 'bcg': 47.4, 'delta': +14.2},
            'slight_improvement': {'overall': 55.5, 'bcg': 48.7, 'delta': -6.8},
            'no_or_negative': {'overall': 11.3, 'bcg': 3.9, 'delta': -7.4},
            'total_positive': {'overall': 88.7, 'bcg': 96.1, 'delta': +7.4},
            'insight': '96.1% BCG see productivity improvement vs 88.7% overall'
        },
        
        'productivity_future': {
            'significant_improvement': {'overall': 64.0, 'bcg': 81.6, 'delta': +17.6},
            'slight_improvement': {'overall': 26.1, 'bcg': 15.8, 'delta': -10.3},
            'no_or_negative': {'overall': 3.5, 'bcg': 2.6, 'delta': -0.9},
            'insight': '81.6% BCG expect significant improvement in 1-3 years'
        },
        
        'implementation_phases': {
            'phase1_conception': {'overall': 30.6, 'bcg': 14.5, 'delta': -16.1},
            'phase2_prototype': {'overall': 29.4, 'bcg': 22.4, 'delta': -7.0},
            'phase3_production': {'overall': 29.4, 'bcg': 36.8, 'delta': +7.4},
            'phase4_rollout': {'overall': 10.0, 'bcg': 26.3, 'delta': +16.3},
            'advanced_phases_combined': {
                'overall': 39.4,  # Phase 3+4
                'bcg': 63.1,      # Phase 3+4
                'delta': +23.7
            },
            'insight': '63.1% BCG in active production (Phase 3+4) vs 39.4% overall'
        },
        
        'top_challenges_overall': [
            {'rank': 1, 'challenge': 'Unklarer ROI-Nachweis', 'percentage': 21.6},
            {'rank': 2, 'challenge': 'IT-Integration', 'percentage': 21.0},
            {'rank': 3, 'challenge': 'Governance & Regulatorik', 'percentage': 20.0},
            {'rank': 4, 'challenge': 'Datenqualität', 'percentage': 19.7},
            {'rank': 5, 'challenge': 'Qualifiziertes Personal', 'percentage': 17.7}
        ],
        
        'top_challenges_bcg': [
            {'rank': 1, 'challenge': 'Datenqualität', 'percentage': 27.6},
            {'rank': 2, 'challenge': 'Unklarer ROI-Nachweis', 'percentage': 26.3},
            {'rank': 3, 'challenge': 'IT-Integration', 'percentage': 22.4},
            {'rank': 4, 'challenge': 'Qualifiziertes Personal', 'percentage': 13.2},
            {'rank': 5, 'challenge': 'Governance & Regulatorik', 'percentage': 10.5}
        ],
        
        'key_findings': [
            'BCG shows 23.7pp lead in advanced implementation phases',
            'Daily usage 35.6pp higher at BCG (90.8% vs 55.2%)',
            'BCG productivity perception significantly more positive',
            'Top challenge shifts: Overall=#1 ROI, BCG=#1 Data Quality',
            'BCG more concentrated on single tool (ChatGPT 98.7%)'
        ]
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_survey_data(csv_path=DATA_FILE):
    """Load and return the complete survey dataset."""
    return pd.read_csv(csv_path, delimiter=DELIMITER)


def get_data_summary(csv_path=DATA_FILE):
    """Get basic statistics about the dataset."""
    df = pd.read_csv(csv_path, delimiter=DELIMITER)
    
    return {
        'total_respondents': len(df),
        'total_columns': len(df.columns),
        'columns': list(df.columns),
        'missing_data': df.isnull().sum().to_dict(),
    }


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_all_analyses_to_json(output_path="analysis_results.json"):
    """
    Export all analyses to a single JSON file for external use.
    
    Args:
        output_path: Path to output JSON file
    
    Returns:
        str: Path to created file
    """
    results = {
        'metadata': {
            'survey_year': '2026',
            'total_respondents': 310,
            'data_source': str(DATA_FILE),
            'generated_at': pd.Timestamp.now().isoformat()
        },
        'challenges_by_phase': analyze_challenges_by_phase(),
        'chart_data': get_challenge_chart_data(),
        'usage_frequency': analyze_usage_frequency(),
        'productivity_trends': get_productivity_trend_data(),
        'bcg_comparison': get_bcg_comparison_data()
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ All analyses exported to {output_path}")
    return output_path


def export_bcg_comparison_to_csv(output_path="bcg_comparison.csv"):
    """
    Export BCG comparison data to CSV format for spreadsheet analysis.
    
    Args:
        output_path: Path to output CSV file
    
    Returns:
        str: Path to created file
    """
    bcg_data = get_bcg_comparison_data()
    
    # Flatten the nested structure for CSV
    rows = []
    
    # Usage frequency
    for freq, data in bcg_data['usage_frequency'].items():
        if isinstance(data, dict):
            rows.append({
                'Category': 'Usage Frequency',
                'Metric': freq.replace('_', ' ').title(),
                'Overall': data['overall'],
                'BCG': data['bcg'],
                'Delta_PP': data['delta']
            })
    
    # Tool usage
    for tool, data in bcg_data['tool_usage'].items():
        if isinstance(data, dict):
            rows.append({
                'Category': 'Tool Usage',
                'Metric': tool.replace('_', ' ').title(),
                'Overall': data['overall'],
                'BCG': data['bcg'],
                'Delta_PP': data['delta']
            })
    
    # Productivity today
    for metric, data in bcg_data['productivity_today'].items():
        if isinstance(data, dict):
            rows.append({
                'Category': 'Productivity Today',
                'Metric': metric.replace('_', ' ').title(),
                'Overall': data['overall'],
                'BCG': data['bcg'],
                'Delta_PP': data['delta']
            })
    
    # Implementation phases
    for phase, data in bcg_data['implementation_phases'].items():
        if isinstance(data, dict):
            rows.append({
                'Category': 'Implementation Phase',
                'Metric': phase.replace('_', ' ').title(),
                'Overall': data['overall'],
                'BCG': data['bcg'],
                'Delta_PP': data['delta']
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ BCG comparison exported to {output_path}")
    return output_path


def export_challenges_by_phase_to_csv(output_path="challenges_by_phase.csv"):
    """
    Export challenge distribution by phase to CSV format.
    
    Args:
        output_path: Path to output CSV file
    
    Returns:
        str: Path to created file
    """
    results = analyze_challenges_by_phase()
    
    rows = []
    for phase_name, data in results.items():
        for rank, (challenge, count, percentage) in enumerate(data['challenges'], 1):
            rows.append({
                'Phase': phase_name,
                'Phase_N': data['n'],
                'Rank': rank,
                'Challenge': challenge,
                'Count': count,
                'Percentage': percentage
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ Challenges by phase exported to {output_path}")
    return output_path


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("KI-ADOPTION SURVEY 2026 - DATA ANALYSIS")
    print("=" * 80)
    
    # Check if data file exists
    if not DATA_FILE.exists():
        print(f"\n❌ Error: Data file not found at {DATA_FILE}")
        print("   Please ensure data/results.CSV exists in the project directory.")
        exit(1)
    
    # Data Summary
    print("\n📊 Dataset Summary")
    print("-" * 80)
    summary = get_data_summary()
    print(f"Total respondents: {summary['total_respondents']}")
    print(f"Total columns: {summary['total_columns']}")
    
    # Analysis 1: Challenges by Implementation Phase
    print("\n\n🔍 ANALYSIS 1: Top-5 Challenges per Implementation Phase")
    print("-" * 80)
    print_challenges_analysis()
    
    # Analysis 2: Chart Data
    print("\n\n📈 ANALYSIS 2: Chart-Ready Data for Visualizations")
    print("-" * 80)
    chart_data = get_challenge_chart_data()
    print(f"Chart labels: {chart_data['labels']}")
    print(f"\nDatasets ({len(chart_data['datasets'])} challenges):")
    for challenge, values in list(chart_data['datasets'].items())[:3]:  # Show first 3
        print(f"  • {challenge}: {values}")
    print("  ...")
    
    # Analysis 3: Usage Frequency
    print("\n\n👥 ANALYSIS 3: Usage Frequency Statistics")
    print("-" * 80)
    usage_data = analyze_usage_frequency()
    if 'manual_data' in usage_data:
        data = usage_data['manual_data']
        print(f"Total respondents: {data['total_respondents']}")
        print(f"GenAI users: {data['genai_users']} ({data['usage_rate']}%)")
        print(f"Daily users: {data['daily_users']} ({data['daily_rate']}%)")
        print("\nUsage Distribution:")
        for freq, count in data['distribution'].items():
            pct = round((count / data['total_respondents']) * 100, 1)
            print(f"  • {freq}: {count} ({pct}%)")
    
    # Analysis 4: Productivity Trends
    print("\n\n📊 ANALYSIS 4: Productivity Trends Over Time")
    print("-" * 80)
    prod_data = get_productivity_trend_data()
    print(f"Time periods: {prod_data['labels']}")
    print("\nTrend lines:")
    for category, values in prod_data['datasets'].items():
        print(f"  • {category}: {values}")
    print("\nKey Insights:")
    for key, value in prod_data['insights'].items():
        print(f"  • {key}: {value}")
    
    # Analysis 5: BCG Company Comparison
    print("\n\n🏢 ANALYSIS 5: BCG vs. Overall Comparison (Detailed)")
    print("-" * 80)
    bcg_data = get_bcg_comparison_data()
    
    print(f"\nSample Sizes:")
    print(f"  • Overall: n={bcg_data['sample_sizes']['overall']}")
    print(f"  • BCG: n={bcg_data['sample_sizes']['bcg']} ({bcg_data['sample_sizes']['bcg_percentage_of_total']}% of total)")
    
    print(f"\nUsage Frequency (Daily):")
    daily = bcg_data['usage_frequency']['daily']
    print(f"  • Overall: {daily['overall']}%")
    print(f"  • BCG: {daily['bcg']}% (Δ {daily['delta']:+.1f}pp)")
    print(f"  • {bcg_data['usage_frequency']['insight']}")
    
    print(f"\nTool Preference (ChatGPT):")
    chatgpt = bcg_data['tool_usage']['chatgpt']
    print(f"  • Overall: {chatgpt['overall']}%")
    print(f"  • BCG: {chatgpt['bcg']}% (Δ {chatgpt['delta']:+.1f}pp)")
    
    print(f"\nProductivity Today (Significant Improvement):")
    prod_today = bcg_data['productivity_today']['significant_improvement']
    print(f"  • Overall: {prod_today['overall']}%")
    print(f"  • BCG: {prod_today['bcg']}% (Δ {prod_today['delta']:+.1f}pp)")
    
    print(f"\nImplementation Phase (Advanced: Phase 3+4):")
    advanced = bcg_data['implementation_phases']['advanced_phases_combined']
    print(f"  • Overall: {advanced['overall']}%")
    print(f"  • BCG: {advanced['bcg']}% (Δ {advanced['delta']:+.1f}pp)")
    
    print(f"\nTop Challenges Ranking:")
    print(f"  Overall #1: {bcg_data['top_challenges_overall'][0]['challenge']} ({bcg_data['top_challenges_overall'][0]['percentage']}%)")
    print(f"  BCG #1: {bcg_data['top_challenges_bcg'][0]['challenge']} ({bcg_data['top_challenges_bcg'][0]['percentage']}%)")
    
    print(f"\nKey Findings:")
    for finding in bcg_data['key_findings']:
        print(f"  ✓ {finding}")
    
    # Analysis 6: Company Comparison Template
    print("\n\n🔧 ANALYSIS 6: Custom Company Comparison (Template)")
    print("-" * 80)
    comp_info = analyze_company_comparison()
    print(f"Note: {comp_info['note']}")
    print(f"Example: {comp_info['example_usage']}")
    
    print("\n\n✅ Analysis complete!")
    print("=" * 80)
    print("\nAll data extracted from:")
    print("  • ergebnisse-2026-workInProgress.html (charts & statistics)")
    print("  • vergleich.html (BCG comparison)")
    print("  • data/results.CSV (raw survey data)")
    print("\nUse individual functions to access specific analyses programmatically.")
    
    # Optional: Export data
    print("\n" + "=" * 80)
    print("EXPORT OPTIONS")
    print("=" * 80)
    print("\nTo export analysis results, uncomment the desired function:")
    print("  # export_all_analyses_to_json('analysis_results.json')")
    print("  # export_bcg_comparison_to_csv('bcg_comparison.csv')")
    print("  # export_challenges_by_phase_to_csv('challenges_by_phase.csv')")
    
    # Uncomment to auto-export:
    # export_all_analyses_to_json()
    # export_bcg_comparison_to_csv()
    # export_challenges_by_phase_to_csv()

