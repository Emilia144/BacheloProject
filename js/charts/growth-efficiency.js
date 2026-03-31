/**
 * growth-efficiency.js — Growth vs. Efficiency charts.
 *
 * Renders:
 *   #growthEfficiencyChart             (line – by implementation phase)
 *   #growthEfficiencyProficiencyChart  (stacked bar – by proficiency level)
 *
 * Expected data shapes:
 *   data.report.charts.growth_by_phase: {
 *     labels_i18n:  [...],           // x-axis phase labels (i18n keys or {de,en})
 *     pct_data:     [[...], ...],    // rows = categories, cols = phases
 *     raw_counts:   [[...], ...]     // same shape, absolute counts
 *   }
 *   data.report.charts.growth_by_proficiency: {
 *     labels_i18n:  [...],           // x-axis proficiency labels
 *     pct_data:     [[...], ...],    // rows = categories, cols = levels
 *     raw_counts:   [[...], ...]     // same shape, absolute counts
 *   }
 *
 * Row order (both charts): [Effizienz, Beides, Wachstum, WederNoch]
 */
(function () {
    'use strict';

    // ── shared constants ──────────────────────────────────
    var C_EFFIZIENZ = '#004A99';
    var C_WACHSTUM  = '#90CAF9';
    var C_WEDERNOCH = '#BEBEBE';

    // i18n keys for the four category series labels
    var CAT_KEYS = [
        'growthEfficiency.cat.efficiency',
        'growthEfficiency.cat.both',
        'growthEfficiency.cat.growth',
        'growthEfficiency.cat.neither'
    ];
    var CAT_FALLBACKS_DE = ['Effizienzhebel', 'Gleichermaßen beides', 'Wachstumstreiber', 'Bisher weder noch'];
    var CAT_FALLBACKS_EN = ['Efficiency Lever', 'Both equally', 'Growth Driver', 'Neither yet'];

    // ── helpers ───────────────────────────────────────────

    function t(key, lang, fallback) {
        if (window.languageManager && window.languageManager.getTranslation) {
            return window.languageManager.getTranslation(key, lang);
        }
        return fallback;
    }

    function resolveLabels(keys, lang) {
        return keys.map(function (key) {
            if (typeof key === 'object') return key[lang] || key.de;
            return t(key, lang, key);
        });
    }

    function getCategoryLabels(lang) {
        var fb = lang === 'en' ? CAT_FALLBACKS_EN : CAT_FALLBACKS_DE;
        return CAT_KEYS.map(function (key, i) {
            return t(key, lang, fb[i]);
        });
    }

    /**
     * Consolidated hatch-pattern utility.
     * Creates a 24×24 diagonal-stripe canvas pattern.
     *
     * @param {string} color1 Foreground stripe color (default C_EFFIZIENZ)
     * @param {string} color2 Background fill color  (default C_WACHSTUM)
     * @returns {CanvasPattern}
     */
    function createHatchPattern(color1, color2) {
        var fg = color1 || C_EFFIZIENZ;
        var bg = color2 || C_WACHSTUM;

        var c = document.createElement('canvas');
        c.width = 24;
        c.height = 24;

        var ctx = c.getContext('2d');
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, 24, 24);
        ctx.fillStyle = fg;

        for (var i = -24; i <= 24; i += 12) {
            ctx.beginPath();
            ctx.moveTo(i, 24);
            ctx.lineTo(i + 3, 24);
            ctx.lineTo(i + 27, 0);
            ctx.lineTo(i + 24, 0);
            ctx.closePath();
            ctx.fill();
        }

        return ctx.createPattern(c, 'repeat');
    }

    // ── growthEfficiencyChart (line – by phase) ──────────

    function initGrowthEfficiencyChart(data, lang) {
        lang = lang || (window.languageManager
            ? window.languageManager.getCurrentLanguage()
            : 'de');

        var src = data && data.report && data.report.charts
            ? data.report.charts.growth_by_phase
            : null;
        if (!src) return null;

        var xLabels   = resolveLabels(src.labels_i18n, lang);
        var catLabels = getCategoryLabels(lang);
        var striped   = createHatchPattern();

        var datasets = [
            {
                label: catLabels[0],
                data: src.pct_data[0],
                rawCounts: src.raw_counts ? src.raw_counts[0] : null,
                borderColor: C_EFFIZIENZ,
                backgroundColor: C_EFFIZIENZ,
                tension: 0.3
            },
            {
                label: catLabels[1],
                data: src.pct_data[1],
                rawCounts: src.raw_counts ? src.raw_counts[1] : null,
                borderColor: striped,
                backgroundColor: striped,
                borderWidth: 3,
                pointRadius: 5.5,
                pointHoverRadius: 7,
                pointBackgroundColor: '#488AC9',
                pointBorderWidth: 0,
                tension: 0.3
            },
            {
                label: catLabels[2],
                data: src.pct_data[2],
                rawCounts: src.raw_counts ? src.raw_counts[2] : null,
                borderColor: C_WACHSTUM,
                backgroundColor: C_WACHSTUM,
                tension: 0.3
            },
            {
                label: catLabels[3],
                data: src.pct_data[3],
                rawCounts: src.raw_counts ? src.raw_counts[3] : null,
                borderColor: C_WEDERNOCH,
                backgroundColor: C_WEDERNOCH,
                tension: 0.3
            }
        ];

        return Shared.renderCombinedLine('growthEfficiencyChart', {
            labels: xLabels,
            datasets: datasets,
            yMax: 60,
            yStepSize: 10,
            tooltipLabel: function (ctx) {
                var raw = ctx.dataset.rawCounts
                    ? ctx.dataset.rawCounts[ctx.dataIndex]
                    : null;
                var suffix = raw != null ? ' (n=' + raw + ')' : '';
                return '  ' + ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(1) + ' %' + suffix;
            }
        });
    }

    // ── growthEfficiencyProficiencyChart (stacked bar – by proficiency) ──

    function initGrowthEfficiencyProficiencyChart(data, lang) {
        lang = lang || (window.languageManager
            ? window.languageManager.getCurrentLanguage()
            : 'de');

        var src = data && data.report && data.report.charts
            ? data.report.charts.growth_by_proficiency
            : null;
        if (!src) return null;

        var xLabels   = resolveLabels(src.labels_i18n, lang);
        var catLabels = getCategoryLabels(lang);
        var striped   = createHatchPattern();

        var catColors = [C_EFFIZIENZ, striped, C_WACHSTUM, C_WEDERNOCH];

        var datasets = catLabels.map(function (label, catIdx) {
            return {
                label: label,
                data: src.pct_data[catIdx],
                backgroundColor: catColors[catIdx],
                rawCounts: src.raw_counts[catIdx]
            };
        });

        var axisXKey = 'growthEfficiency.proficiency.axisX';
        var axisYKey = 'growthEfficiency.proficiency.axisY';
        var axisX = t(axisXKey, lang, lang === 'en' ? 'GenAI Proficiency' : 'GenAI-Kompetenz');
        var axisY = t(axisYKey, lang, lang === 'en' ? 'Share of respondents' : 'Anteil der Befragten');

        return Shared.renderStackedBar('growthEfficiencyProficiencyChart', {
            labels: xLabels,
            datasets: datasets,
            axisTitles: { x: axisX, y: axisY }
        });
    }

    // ── public API ────────────────────────────────────────
    window.initGrowthEfficiencyChart = initGrowthEfficiencyChart;
    window.initGrowthEfficiencyProficiencyChart = initGrowthEfficiencyProficiencyChart;
    window.createHatchPattern = createHatchPattern;
})();
