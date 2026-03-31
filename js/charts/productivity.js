/**
 * productivity.js — Productivity timeline line chart with forecast overlay.
 *
 * Renders #productivityChart using data from
 * window.DATA.report.charts.productivity_timeline
 *
 * Expected shape:
 *   {
 *     labels:              ['2024 / 25', '2026 (heute)', '2026 (in 1–3 J.)'],
 *     forecast_from_index: 1,
 *     datasets: [
 *       { label_i18n, values, color, border_dash? }
 *     ]
 *   }
 */
(function () {
    'use strict';

    // Module-level language state — updated on every (re-)render
    let currentLang = 'de';

    // Cached forecast_from_index — updated on every render
    let forecastFromIndex = 1;

    // ── forecast background plugin ────────────────────────
    var forecastBgPlugin = {
        id: 'forecastBg',
        beforeDraw: function (chart) {
            var ctx = chart.ctx;
            var ca  = chart.chartArea;
            var xs  = chart.scales.x;

            // forecastFromIndex=0 means the full domain is forecast (divider at start).
            var xMid;
            if (forecastFromIndex <= 0) {
                xMid = ca.left;
            } else {
                xMid = (xs.getPixelForValue(forecastFromIndex - 1) +
                        xs.getPixelForValue(forecastFromIndex)) / 2;
            }

            // Shaded region
            ctx.save();
            ctx.fillStyle = '#F7FAFF';
            ctx.fillRect(xMid, ca.top, ca.right - xMid, ca.bottom - ca.top);

            // Dashed divider line
            ctx.strokeStyle = '#D5EAFB';
            ctx.lineWidth = 1;
            ctx.setLineDash([5, 4]);
            if (forecastFromIndex > 0) {
                ctx.beginPath();
                ctx.moveTo(xMid, ca.top);
                ctx.lineTo(xMid, ca.bottom);
                ctx.stroke();
            }
            ctx.setLineDash([]);

            // "ERWARTUNG" / "FORECAST" label
            var forecastLabel = currentLang === 'en' ? 'FORECAST' : 'ERWARTUNG';
            ctx.fillStyle = '#B4CFE6';
            ctx.font = '600 10px "Open Sans", sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(forecastLabel, (xMid + ca.right) / 2, ca.top + 12);
            ctx.restore();
        }
    };

    function configureForecastBgPlugin(lang, forecastIndex) {
        if (lang) currentLang = lang;
        if (forecastIndex != null) forecastFromIndex = forecastIndex;
    }

    // ── init ──────────────────────────────────────────────
    function initProductivityChart(data, lang) {
        currentLang = lang || (window.languageManager
            ? window.languageManager.getCurrentLanguage()
            : 'de');

        var src = data && data.report && data.report.charts
            ? data.report.charts.productivity_timeline
            : null;
        if (!src) return null;

        forecastFromIndex = src.forecast_from_index != null
            ? src.forecast_from_index
            : 1;
        configureForecastBgPlugin(currentLang, forecastFromIndex);

        var labels = src.labels.map(function (l) {
            return (typeof l === 'object') ? (l[currentLang] || l.de) : l;
        });

        var style = getComputedStyle(document.documentElement);
        var thBlue = style.getPropertyValue('--th-blue').trim() || '#1565C0';

        var datasets = src.datasets.map(function (ds, i) {
            var label = window.languageManager
                ? window.languageManager.getTranslation(ds.label_i18n, currentLang)
                : ds.label_i18n;

            var out = {
                label: label,
                data: ds.values,
                borderColor: ds.color === 'var(--th-blue)' ? thBlue : ds.color,
                order: i
            };

            if (ds.border_dash) {
                out.borderDash = ds.border_dash;
            }

            return out;
        });

        return Shared.renderCombinedLine('productivityChart', {
            labels: labels,
            datasets: datasets,
            yMax: 100,
            yStepSize: 20,
            plugins: [forecastBgPlugin],
            tooltipLabel: function (ctx) {
                return '  ' + ctx.dataset.label + ': ' + ctx.parsed.y + ' %';
            }
        });
    }

    window.initProductivityChart = initProductivityChart;
    window.forecastBgPlugin = forecastBgPlugin;
    window.configureForecastBgPlugin = configureForecastBgPlugin;
})();
