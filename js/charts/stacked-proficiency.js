/**
 * stacked-proficiency.js — Stacked proficiency × productivity bar charts.
 *
 * Renders #stackedTodayChart and #stackedFutureChart using data from
 * window.DATA.report.charts.stacked_proficiency
 *
 * Expected shape:
 *   {
 *     today:  { labels_i18n: [...], pct_data: [[...]], raw_data: [[...]], category_labels_i18n: [...] },
 *     future: { labels_i18n: [...], pct_data: [[...]], raw_data: [[...]], category_labels_i18n: [...] }
 *   }
 *
 * category_labels_i18n  – i18n keys for the four stacked categories
 *                         (e.g. "proficiency.cat.negative", …)
 * labels_i18n           – i18n keys for x-axis proficiency levels
 * pct_data              – already normalised percentages [rows × 4]
 * raw_data              – absolute counts            [rows × 4]
 */
(function () {
    'use strict';

    var CAT_COLORS = ['#D32F2F', '#BEBEBE', '#90CAF9', '#42A5F5'];

    /* ── helper: resolve an array of i18n keys ── */
    function resolveLabels(keys, lang) {
        return keys.map(function (key) {
            if (typeof key === 'object') return key[lang] || key.de;
            if (window.languageManager) {
                return window.languageManager.getTranslation(key, lang);
            }
            return key;
        });
    }

    /* ── factory: build datasets + call Shared.renderStackedBar ── */
    function makeStackedChart(canvasId, subset, lang) {
        var xLabels = resolveLabels(subset.labels_i18n, lang);
        var catLabels = resolveLabels(subset.category_labels_i18n, lang);

        var datasets = catLabels.map(function (catLabel, catIdx) {
            return {
                label: catLabel,
                data: subset.pct_data.map(function (row) { return row[catIdx]; }),
                backgroundColor: CAT_COLORS[catIdx],
                rawCounts: subset.raw_data.map(function (row) { return row[catIdx]; })
            };
        });

        var axisXKey = 'results2026.findings.proficiencyProductivity.axisX';
        var axisYKey = 'results2026.findings.proficiencyProductivity.axisY';
        var axisX = window.languageManager
            ? window.languageManager.getTranslation(axisXKey, lang)
            : (lang === 'en' ? 'GenAI Proficiency' : 'GenAI-Kompetenz');
        var axisY = window.languageManager
            ? window.languageManager.getTranslation(axisYKey, lang)
            : (lang === 'en' ? 'Share of respondents' : 'Anteil der Befragten');

        return Shared.renderStackedBar(canvasId, {
            labels: xLabels,
            datasets: datasets,
            axisTitles: { x: axisX, y: axisY }
        });
    }

    /* ── public entry point ── */
    function initStackedProficiencyCharts(data, lang) {
        lang = lang || (window.languageManager
            ? window.languageManager.getCurrentLanguage()
            : 'de');

        var src = data && data.report && data.report.charts
            ? data.report.charts.stacked_proficiency
            : null;
        if (!src) return;

        makeStackedChart('stackedTodayChart', src.today, lang);
        makeStackedChart('stackedFutureChart', src.future, lang);
    }

    window.initStackedProficiencyCharts = initStackedProficiencyCharts;
})();
