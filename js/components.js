/**
 * TH Brandenburg - Reusable UI Components Library
 * =================================================
 * 
 * This library provides JavaScript functions to generate consistent HTML components
 * across all pages. Each function returns an HTML string that can be inserted
 * into the DOM using innerHTML or similar methods.
 * 
 * Usage:
 *   document.getElementById('target').innerHTML = UIComponents.kpiCard({...});
 * 
 * All components support i18n via data-i18n attributes where applicable.
 */

const UIComponents = {

    // ============================================================================
    // KPI CARDS
    // ============================================================================

    /**
     * KPI Card - Displays a key performance indicator with value, benchmark, and delta
     * 
     * @param {Object} config - Configuration object
     * @param {string} config.title - Card title (supports i18n key)
     * @param {number} config.value - Main value to display
     * @param {string} [config.unit='%'] - Unit symbol (e.g., '%', 'x', '')
     * @param {string} config.subtitle - Subtitle text (e.g., "Unternehmen", "BCG")
     * @param {number} config.benchmark - Benchmark value for comparison
     * @param {string} [config.benchmarkLabel='Gesamt'] - Label for benchmark
     * @param {number} config.delta - Difference (percentage points)
     * @param {string} [config.titleI18n] - Optional i18n key for title
     * @returns {string} HTML string for KPI card
     * 
     * @example
     * UIComponents.kpiCard({
     *   title: 'Tägliche Nutzung',
     *   value: 90.8,
     *   unit: '%',
     *   subtitle: 'BCG',
     *   benchmark: 55.2,
     *   benchmarkLabel: 'Gesamt',
     *   delta: 35.6
     * })
     */
    kpiCard: (config) => {
        const {
            title,
            value,
            unit = '%',
            subtitle,
            benchmark,
            benchmarkLabel = 'Gesamt',
            delta,
            titleI18n
        } = config;

        const deltaClass = delta > 0 ? 'cmp-delta--pos' : delta < 0 ? 'cmp-delta--neg' : 'cmp-delta--neu';
        const deltaSymbol = delta > 0 ? '+' : delta < 0 ? '−' : '±';
        const deltaAbs = Math.abs(delta);
        const titleAttr = titleI18n ? `data-i18n="${titleI18n}"` : '';

        return `
            <div class="kpi-card">
                <div class="kpi-card__title" ${titleAttr}>${title}</div>
                <div class="kpi-card__value" style="color:#004A99;">${value.toFixed(1)}<span>${unit}</span></div>
                <div class="kpi-card__sub">${subtitle}</div>
                <div class="kpi-card__bench">${benchmarkLabel}: ${benchmark.toFixed(1)}${unit}</div>
                <div class="kpi-card__delta ${deltaClass}">${deltaSymbol}&thinsp;${deltaAbs.toFixed(1)}&thinsp;PP</div>
            </div>
        `;
    },

    // ============================================================================
    // COMPARISON BARS
    // ============================================================================

    /**
     * Comparison Bar - Side-by-side horizontal bars comparing two values
     * 
     * @param {Object} config - Configuration object
     * @param {string} config.label - Label for the metric
     * @param {number} config.overallValue - Overall/benchmark value (0-100)
     * @param {number} config.companyValue - Company/specific value (0-100)
     * @param {number} config.delta - Difference in percentage points
     * @param {string} [config.overallLabel='Alle'] - Label for overall/benchmark
     * @param {string} [config.companyLabel='Unternehmen'] - Label for company/specific
     * @param {string} [config.labelI18n] - Optional i18n key for label
     * @returns {string} HTML string for comparison bar
     */
    comparisonBar: (config) => {
        const {
            label,
            overallValue,
            companyValue,
            delta,
            overallLabel = 'Alle',
            companyLabel = 'Unternehmen',
            labelI18n
        } = config;

        const deltaClass = delta > 0 ? 'cmp-delta--pos' : delta < 0 ? 'cmp-delta--neg' : 'cmp-delta--neu';
        const deltaSymbol = delta > 0 ? '+' : delta < 0 ? '−' : '±';
        const deltaAbs = Math.abs(delta);
        const labelAttr = labelI18n ? `data-i18n="${labelI18n}"` : '';

        return `
                    <div class="cmp-row">
                        <div class="cmp-row__header">
                            <span class="cmp-row__label" ${labelAttr}>${label}</span>
                            <span class="cmp-delta ${deltaClass}">${deltaSymbol}&thinsp;${deltaAbs.toFixed(1)}&thinsp;PP</span>
                        </div>
                        <div class="cmp-bars">
                            <div class="cmp-bar-row">
                                <span class="cmp-bar-row__who">${overallLabel}</span>
                                <div class="cmp-bar-row__track"><div class="cmp-bar-row__fill fill--bench" style="width:${overallValue}%;"></div></div>
                                <span class="cmp-bar-row__val" style="color:#1565C0;">${overallValue.toFixed(1)}&thinsp;%</span>
                            </div>
                            <div class="cmp-bar-row">
                                <span class="cmp-bar-row__who" style="font-weight:600;color:var(--th-blue);">${companyLabel}</span>
                                <div class="cmp-bar-row__track"><div class="cmp-bar-row__fill fill--company" style="width:${companyValue}%;"></div></div>
                                <span class="cmp-bar-row__val" style="color:#004A99;">${companyValue.toFixed(1)}&thinsp;%</span>
                            </div>
                        </div>
                    </div>
        `;
    },

    // ============================================================================
    // PROGRESS BARS
    // ============================================================================

    /**
     * Progress Bar - Single horizontal bar with label and percentage
     * 
     * @param {Object} config - Configuration object
     * @param {string} config.label - Label text
     * @param {number} config.value - Percentage value (0-100)
     * @param {string} [config.color='var(--th-blue)'] - Bar color
     * @param {boolean} [config.showCount=false] - Show count in addition to percentage
     * @param {number} [config.count] - Absolute count (if showCount is true)
     * @param {string} [config.labelI18n] - Optional i18n key for label
     * @returns {string} HTML string for progress bar
     */
    progressBar: (config) => {
        const {
            label,
            value,
            color = 'var(--th-blue)',
            showCount = false,
            count,
            labelI18n
        } = config;

        const labelAttr = labelI18n ? `data-i18n="${labelI18n}"` : '';
        const displayValue = showCount && count !== undefined 
            ? `<strong>${count} (${Math.round(value)}%)</strong>`
            : `<strong style="color:${color};">${Math.round(value)}%</strong>`;

        return `
            <div>
                <div style="display:flex;justify-content:space-between;margin-bottom:0.25rem;padding:0 0.25rem;">
                    <span style="font-weight:500;" ${labelAttr}>${label}</span>
                    ${displayValue}
                </div>
                <div style="width:100%;height:8px;background:#E0E0E0;border-radius:4px;overflow:hidden;">
                    <div style="width:${value}%;height:100%;background:${color};border-radius:4px;"></div>
                </div>
            </div>
        `;
    },

    // ============================================================================
    // FEATURED CARDS
    // ============================================================================

    /**
     * Featured Card - Large card with icon, title, and custom body content
     * 
     * @param {Object} config - Configuration object
     * @param {string} config.title - Card title
     * @param {string} config.icon - Lucide icon name (e.g., 'trending-up', 'layers')
     * @param {string} config.bodyContent - HTML content for card body
     * @param {string} [config.titleI18n] - Optional i18n key for title
     * @param {string} [config.marginBottom='2.5rem'] - Bottom margin
     * @returns {string} HTML string for featured card
     */
    featuredCard: (config) => {
        const {
            title,
            icon,
            bodyContent,
            titleI18n,
            marginBottom = '2.5rem'
        } = config;

        const titleAttr = titleI18n ? `data-i18n="${titleI18n}"` : '';

        return `
            <div class="card card--featured" style="margin-bottom:${marginBottom};">
                <div class="card__header">
                    <h3 class="card__title" style="display:flex;align-items:center;gap:0.75rem;">
                        <i data-lucide="${icon}" style="width:1.5rem;height:1.5rem;color:var(--th-blue);"></i>
                        <span ${titleAttr}>${title}</span>
                    </h3>
                </div>
                <div class="card__body">
                    ${bodyContent}
                </div>
            </div>
        `;
    },

    /**
     * Simple Card - Basic card without icon, just title and body
     * 
     * @param {Object} config - Configuration object
     * @param {string} config.title - Card title
     * @param {string} config.bodyContent - HTML content for card body
     * @param {string} [config.titleI18n] - Optional i18n key for title
     * @param {string} [config.marginBottom='2.5rem'] - Bottom margin
     * @returns {string} HTML string for simple card
     */
    simpleCard: (config) => {
        const {
            title,
            bodyContent,
            titleI18n,
            marginBottom = '2.5rem'
        } = config;

        const titleAttr = titleI18n ? `data-i18n="${titleI18n}"` : '';

        return `
            <div class="card" style="margin-bottom:${marginBottom};">
                <div class="card__header">
                    <h3 class="card__title" ${titleAttr}>${title}</h3>
                </div>
                <div class="card__body">
                    ${bodyContent}
                </div>
            </div>
        `;
    },

    // ============================================================================
    // STAT CARDS
    // ============================================================================

    /**
     * Stat Card - Display a single statistic with large value and label
     * 
     * @param {Object} config - Configuration object
     * @param {number|string} config.value - Main value to display
     * @param {string} [config.unit=''] - Unit symbol (e.g., '%', 'x')
     * @param {string} config.label - Label text below value
     * @param {string} [config.labelI18n] - Optional i18n key for label
     * @param {string} [config.valueColor='var(--th-blue)'] - Color for value
     * @returns {string} HTML string for stat card
     */
    statCard: (config) => {
        const {
            value,
            unit = '',
            label,
            labelI18n,
            valueColor = 'var(--th-blue)'
        } = config;

        const labelAttr = labelI18n ? `data-i18n="${labelI18n}"` : '';
        const unitSpan = unit ? `<span>${unit}</span>` : '';

        return `
            <div class="stat-card">
                <div class="stat-card__value" style="color:${valueColor};">${value}${unitSpan}</div>
                <div class="stat-card__label" ${labelAttr}>${label}</div>
            </div>
        `;
    },

    // ============================================================================
    // INSIGHT BOXES
    // ============================================================================

    /**
     * Insight Box - Highlighted box for key insights or analysis
     * 
     * @param {Object} config - Configuration object
     * @param {string} config.content - HTML content for insight
     * @param {string} [config.borderColor='var(--th-blue)'] - Left border color
     * @param {string} [config.backgroundColor='#EEF5FF'] - Background color
     * @param {string} [config.title] - Optional title/header
     * @param {string} [config.titleI18n] - Optional i18n key for title
     * @returns {string} HTML string for insight box
     */
    insightBox: (config) => {
        const {
            content,
            borderColor = 'var(--th-blue)',
            backgroundColor = '#EEF5FF',
            title,
            titleI18n
        } = config;

        const titleHtml = title ? `
            <h4 style="margin-bottom:0.75rem;font-size:0.95rem;color:${borderColor};" ${titleI18n ? `data-i18n="${titleI18n}"` : ''}>${title}</h4>
        ` : '';

        return `
            <div style="padding:1.25rem 1.5rem;background:${backgroundColor};border-radius:0.5rem;border-left:4px solid ${borderColor};">
                ${titleHtml}
                <p style="margin:0;font-size:0.875rem;color:var(--th-gray);line-height:1.7;">${content}</p>
            </div>
        `;
    },

    // ============================================================================
    // PHASE CARDS
    // ============================================================================

    /**
     * Phase Card - Implementation phase card with percentage and challenge
     * 
     * @param {Object} config - Configuration object
     * @param {number} config.phaseNumber - Phase number (1-4)
     * @param {string} config.phaseName - Phase name
     * @param {number} config.percentage - Percentage of respondents
     * @param {string} config.challenge - Top challenge for this phase
     * @param {number} config.challengePercentage - Percentage facing this challenge
     * @param {string} [config.phaseNameI18n] - Optional i18n key for phase name
     * @param {string} [config.challengeI18n] - Optional i18n key for challenge
     * @param {boolean} [config.isActive=false] - Whether this is active/advanced phase
     * @returns {string} HTML string for phase card
     */
    phaseCard: (config) => {
        const {
            phaseNumber,
            phaseName,
            percentage,
            challenge,
            challengePercentage,
            phaseNameI18n,
            challengeI18n,
            isActive = false
        } = config;

        const phaseNameAttr = phaseNameI18n ? `data-i18n="${phaseNameI18n}"` : '';
        const challengeAttr = challengeI18n ? `data-i18n="${challengeI18n}"` : '';

        // Color scheme based on phase
        let borderColor, backgroundColor, valueColor, challengeBg, challengeBorder, challengeTextColor;
        
        if (isActive) {
            borderColor = phaseNumber === 4 ? '2px solid var(--th-blue)' : '1px solid #90CAF9';
            backgroundColor = '#EEF5FF';
            valueColor = 'var(--th-blue)';
            challengeBg = phaseNumber === 4 ? 'var(--th-blue)' : '#E3F2FD';
            challengeBorder = phaseNumber === 4 ? 'none' : '1px solid #90CAF9';
            challengeTextColor = phaseNumber === 4 ? 'white' : '#1565C0';
        } else {
            borderColor = '1px solid #E0E0E0';
            backgroundColor = '#FAFAFA';
            valueColor = '#FF9800';
            challengeBg = '#FFF3E0';
            challengeBorder = '1px solid #FFE0B2';
            challengeTextColor = '#E65100';
        }

        return `
        <div style="border:${borderColor};border-radius:0.5rem;padding:1.25rem;text-align:center;background:${backgroundColor};">
            <div style="font-size:0.7rem;font-weight:600;color:var(--th-gray);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem;">Phase ${phaseNumber}</div>
            <div style="font-size:0.875rem;font-weight:600;color:var(--th-blue);margin-bottom:0.75rem;line-height:1.35;" ${phaseNameAttr}>${phaseName}</div>
            <div style="font-size:1.75rem;font-weight:700;color:${valueColor};line-height:1;margin-bottom:0.25rem;">${percentage}%</div>
            <div style="font-size:0.75rem;color:var(--th-gray);margin-bottom:1rem;">der Befragten</div>
            <div style="padding:0.5rem 0.75rem;background:${challengeBg};border-radius:0.375rem;border:${challengeBorder};">
                <div style="font-size:0.68rem;color:${challengeTextColor};font-weight:600;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:0.2rem;">Top-Herausforderung</div>
                <div style="font-size:0.8125rem;font-weight:700;color:${challengeTextColor};" ${challengeAttr}>${challenge}</div>
                <div style="font-size:0.72rem;color:${challengeTextColor};margin-top:0.1rem;">${challengePercentage} % in dieser Phase</div>
            </div>
        </div>
        `;
    },

    // ============================================================================
    // CHART CONTAINERS
    // ============================================================================

    /**
     * Chart Container - Wrapper for Chart.js charts with title and subtitle
     * 
     * @param {Object} config - Configuration object
     * @param {string} config.canvasId - ID for the canvas element
     * @param {string} config.title - Chart title
     * @param {string} config.subtitle - Chart subtitle/description
     * @param {string} [config.insightText] - Optional insight text below chart
     * @param {string} [config.titleI18n] - Optional i18n key for title
     * @param {string} [config.subtitleI18n] - Optional i18n key for subtitle
     * @param {string} [config.insightI18n] - Optional i18n key for insight
     * @param {number} [config.height=300] - Canvas height in pixels
     * @returns {string} HTML string for chart container
     */
    chartContainer: (config) => {
        const {
            canvasId,
            title,
            subtitle,
            insightText,
            titleI18n,
            subtitleI18n,
            insightI18n,
            height = 300
        } = config;

        const titleAttr = titleI18n ? `data-i18n="${titleI18n}"` : '';
        const subtitleAttr = subtitleI18n ? `data-i18n="${subtitleI18n}"` : '';
        const insightAttr = insightI18n ? `data-i18n="${insightI18n}" data-i18n-html="true"` : '';

        const insightHtml = insightText ? `
            <p style="margin:1.125rem 0 0 0;font-size:0.875rem;line-height:1.6;color:var(--th-gray);padding-top:1rem;border-top:1px solid #F0F0F0;" ${insightAttr}>
                ${insightText}
            </p>
        ` : '';

        return `
        <div style="border:1px solid #E0E0E0;border-radius:0.5rem;overflow:hidden;">
            <div style="padding:1rem 1.5rem;border-bottom:1px solid #E0E0E0;background:#F9FAFB;">
                <h4 style="margin:0 0 0.25rem 0;font-size:0.95rem;color:var(--th-blue);font-weight:600;" ${titleAttr}>${title}</h4>
                <p style="margin:0;font-size:0.8rem;color:var(--th-gray);" ${subtitleAttr}>${subtitle}</p>
            </div>
            <div style="padding:1.5rem 1.5rem 1rem;">
                <div style="position:relative;height:${height}px;">
                    <canvas id="${canvasId}"></canvas>
                </div>
                ${insightHtml}
            </div>
        </div>
        `;
    },

    // ============================================================================
    // COMPARISON CARDS (Before/After)
    // ============================================================================

    /**
     * Comparison Card - Side-by-side comparison (e.g., 2024 vs 2026)
     * 
     * @param {Object} config - Configuration object
     * @param {string} config.metric - Metric name
     * @param {Object} config.before - Before data {year, value, description}
     * @param {Object} config.after - After data {year, value, description}
     * @param {number} config.delta - Change in percentage points
     * @param {string} [config.metricI18n] - Optional i18n key for metric
     * @returns {string} HTML string for comparison card
     */
    comparisonCard: (config) => {
        const {
            metric,
            before,
            after,
            delta,
            metricI18n
        } = config;

        const metricAttr = metricI18n ? `data-i18n="${metricI18n}"` : '';
        const deltaSymbol = delta > 0 ? '↗' : delta < 0 ? '↘' : '→';
        const deltaText = delta > 0 ? `+${Math.round(delta)}pp` : `${Math.round(delta)}pp`;

        return `
        <div style="border:2px solid #E0E0E0;border-radius:0.5rem;padding:1.5rem;text-align:center;">
            <div style="font-size:0.8rem;font-weight:600;color:var(--th-gray);margin-bottom:1rem;text-transform:uppercase;" ${metricAttr}>${metric}</div>
            <div style="display:flex;flex-direction:column;gap:0.75rem;">
                <div style="background:#EEF5FF;padding:0.75rem;border-radius:0.375rem;">
                    <div style="font-size:0.75rem;color:var(--th-gray);">${after.year}</div>
                    <div style="font-size:1.25rem;font-weight:700;color:var(--th-blue);">${after.value}%</div>
                </div>
                <div style="color:var(--th-blue);font-weight:600;font-size:0.9rem;">${deltaSymbol} ${deltaText}</div>
                <div style="background:#F5F5F5;padding:0.75rem;border-radius:0.375rem;">
                    <div style="font-size:0.75rem;color:var(--th-gray);">${before.year}</div>
                    <div style="font-size:1.25rem;font-weight:700;color:#FF9800;">${before.value}%</div>
                </div>
            </div>
        </div>
        `;
    },

    // ============================================================================
    // GRID LAYOUTS
    // ============================================================================

    /**
     * Grid Container - Responsive grid wrapper
     * 
     * @param {Object} config - Configuration object
     * @param {string} config.content - HTML content to place in grid
     * @param {number} [config.columns=2] - Number of columns
     * @param {string} [config.gap='1.5rem'] - Gap between items
     * @param {string} [config.marginBottom='2.5rem'] - Bottom margin
     * @returns {string} HTML string for grid container
     */
    grid: (config) => {
        const {
            content,
            columns = 2,
            gap = '1.5rem',
            marginBottom = '2.5rem'
        } = config;

        const gridClass = columns === 3 ? 'grid grid--3' : 'grid grid--2';

        return `
        <div class="${gridClass}" style="gap:${gap};margin-bottom:${marginBottom};">
            ${content}
        </div>
        `;
    },

    // ============================================================================
    // SECTION LABELS
    // ============================================================================

    /**
     * Section Label - Decorative label with horizontal lines
     * 
     * @param {Object} config - Configuration object
     * @param {string} config.text - Label text
     * @param {string} [config.textI18n] - Optional i18n key
     * @returns {string} HTML string for section label
     */
    sectionLabel: (config) => {
        const { text, textI18n } = config;
        const textAttr = textI18n ? `data-i18n="${textI18n}"` : '';

        return `
        <div class="section-label">
            <span class="section-label__line"></span>
            <span class="small-caps" ${textAttr}>${text}</span>
            <span class="section-label__line"></span>
        </div>
        `;
    },

    // ============================================================================
    // UTILITY FUNCTIONS
    // ============================================================================

    /**
     * Generate multiple comparison bars at once
     * @param {Array<Object>} bars - Array of bar configurations
     * @returns {string} HTML string for all bars
     */
    comparisonBars: (bars) => {
        return bars.map(bar => UIComponents.comparisonBar(bar)).join('\n');
    },

    /**
     * Generate multiple progress bars at once
     * @param {Array<Object>} bars - Array of progress bar configurations
     * @returns {string} HTML string for all bars wrapped in container
     */
    progressBars: (bars) => {
        const barsHtml = bars.map(bar => UIComponents.progressBar(bar)).join('\n');
        return `
        <div style="display:flex;flex-direction:column;gap:1rem;">
            ${barsHtml}
        </div>
        `;
    },

    /**
     * Generate KPI card grid
     * @param {Array<Object>} cards - Array of KPI card configurations
     * @param {number} [columns=3] - Number of columns
     * @returns {string} HTML string for KPI cards in grid
     */
    kpiCardGrid: (cards, columns = 3) => {
        const cardsHtml = cards.map(card => UIComponents.kpiCard(card)).join('\n');
        return UIComponents.grid({
            content: cardsHtml,
            columns: columns
        });
    },

    /**
     * Generate stat card grid
     * @param {Array<Object>} cards - Array of stat card configurations
     * @param {number} [columns=2] - Number of columns
     * @returns {string} HTML string for stat cards in grid
     */
    statCardGrid: (cards, columns = 2) => {
        const cardsHtml = cards.map(card => UIComponents.statCard(card)).join('\n');
        return `
        <div class="stats-grid" style="grid-template-columns:repeat(${columns}, 1fr);">
            ${cardsHtml}
        </div>
        `;
    }
};

// Make available globally
if (typeof window !== 'undefined') {
    window.UIComponents = UIComponents;
}

// Export for module systems (optional)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIComponents;
}
