/**
 * challenges.js — Challenges-by-stage line chart.
 *
 * Renders #challengesChart using data from
 * window.DATA.report.charts.challenges_by_stage
 *
 * Expected shape:
 *   {
 *     labels: [ { de: "...", en: "..." }, ... ],
 *     datasets: [
 *       { label_i18n: "challenges.roi", values: [25.3, ...], color: "#D32F2F" },
 *       ...
 *     ]
 *   }
 */
(function () {
    'use strict';

    function initChallengesChart(data, lang) {
        lang = lang || (window.languageManager
            ? window.languageManager.getCurrentLanguage()
            : 'de');

        var src = data && data.report && data.report.charts
            ? data.report.charts.challenges_by_stage
            : null;
        if (!src) return null;

        var labels = src.labels.map(function (l) {
            if (typeof l === 'object') return l[lang] || l.de;
            if (window.languageManager) return window.languageManager.getTranslation(l, lang);
            return l;
        });

        var datasets = src.datasets.map(function (ds, i) {
            var label = window.languageManager
                ? window.languageManager.getTranslation(ds.label_i18n, lang)
                : ds.label_i18n;

            return {
                label: label,
                data: ds.values,
                borderColor: ds.color,
                order: i + 1
            };
        });

        return Shared.renderCombinedLine('challengesChart', {
            labels: labels,
            datasets: datasets,
            yMax: 40,
            yStepSize: 10
        });
    }

    window.initChallengesChart = initChallengesChart;
})();
