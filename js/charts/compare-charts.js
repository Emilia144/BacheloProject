/**
 * compare-charts.js — Comparative charts for vergleich.html.
 *
 * Exports:
 *   window.initCompareProductivityChart(chartData, lang)
 *   window.initCompareGrowthEfficiencyChart(chartData, lang)
 */
(function () {
    'use strict';

    var FONT = "'Open Sans', sans-serif";

    function t(key, lang, fallback) {
        if (window.languageManager && window.languageManager.getTranslation) {
            return window.languageManager.getTranslation(key, lang);
        }
        return fallback || key;
    }

    function resolveLabel(label, lang) {
        if (label && typeof label === 'object') return label[lang] || label.de;
        return label;
    }

    function resolveTimelineSource(chartData) {
        if (!chartData) return null;
        if (chartData.charts && chartData.charts.productivity_timeline) {
            return chartData.charts.productivity_timeline;
        }
        if (chartData.productivity_timeline) {
            return chartData.productivity_timeline;
        }
        return null;
    }

    function resolveGrowthSource(chartData) {
        if (!chartData) return null;
        if (chartData.charts && chartData.charts.growth_efficiency) {
            return chartData.charts.growth_efficiency;
        }
        if (chartData.growth_efficiency) {
            return chartData.growth_efficiency;
        }
        if (chartData.sections && chartData.sections.growth_efficiency) {
            return chartData.sections.growth_efficiency;
        }
        return null;
    }

    function initCompareProductivityChart(chartData, lang) {
        lang = lang || (window.languageManager
            ? window.languageManager.getCurrentLanguage()
            : 'de');

        var src = resolveTimelineSource(chartData);
        if (!src) return null;

        if (window.productivityChart && typeof window.productivityChart.destroy === 'function') {
            window.productivityChart.destroy();
            window.productivityChart = null;
        }

        var labels = (src.labels || []).map(function (l) {
            return resolveLabel(l, lang);
        });

        var style = getComputedStyle(document.documentElement);
        var thBlue = style.getPropertyValue('--th-blue').trim() || '#1565C0';

        var FALLBACK_COLORS = [thBlue, '#90CAF9', '#BEBEBE'];

        var datasets = (src.datasets || []).map(function (ds, i) {
            var label = ds.label;
            if (!label && ds.label_i18n) {
                label = t(ds.label_i18n, lang, ds.label_i18n);
            }

            var rawColor = ds.color || FALLBACK_COLORS[i] || '#999999';
            var resolvedColor = rawColor === 'var(--th-blue)' ? thBlue : rawColor;

            var out = {
                label: label || ('Series ' + (i + 1)),
                data: ds.values || [],
                borderColor: resolvedColor,
                order: i + 1
            };

            if (ds.border_dash) {
                out.borderDash = ds.border_dash;
            }
            return out;
        });

        var fIdx = src.forecast_from_index != null ? src.forecast_from_index : 2;
        if (typeof window.configureForecastBgPlugin === 'function') {
            window.configureForecastBgPlugin(lang, fIdx);
        }

        if (window.Shared && typeof window.Shared.renderCombinedLine === 'function') {
            window.productivityChart = window.Shared.renderCombinedLine('productivityChart', {
                labels: labels,
                datasets: datasets,
                yMax: 100,
                yStepSize: 20,
                plugins: window.forecastBgPlugin ? [window.forecastBgPlugin] : undefined,
                tooltipLabel: function (ctx) {
                    return '  ' + ctx.dataset.label + ': ' + ctx.parsed.y + ' %';
                }
            });
        }

        return window.productivityChart;
    }

    function buildGrowthChartPayload(src, chartData, lang) {
        if (Array.isArray(src)) {
            var meta = chartData && chartData.meta ? chartData.meta : {};
            var benchLabel = 'Alle (n=' + (meta.n_benchmark != null ? meta.n_benchmark : '?') + ')';
            var companyName = meta.display || meta.name || 'Unternehmen';
            var companyLabel = companyName + ' (n=' + (meta.n_company != null ? meta.n_company : '?') + ')';

            return {
                labels: src.map(function (d) { return d.label; }),
                datasets: [
                    {
                        label: benchLabel,
                        values: src.map(function (d) { return d.bench_value; }),
                        color: '#90CAF9'
                    },
                    {
                        label: companyLabel,
                        values: src.map(function (d) { return d.company_value; }),
                        color: '#004A99'
                    }
                ]
            };
        }

        var labels = (src.labels || src.labels_i18n || []).map(function (l) {
            return resolveLabel(l, lang);
        });
        var datasets = (src.datasets || []).map(function (ds) {
            return {
                label: ds.label || t(ds.label_i18n, lang, ds.label_i18n),
                values: ds.values || ds.data || [],
                color: ds.color || '#90CAF9'
            };
        });

        return { labels: labels, datasets: datasets };
    }

    function initCompareGrowthEfficiencyChart(chartData, lang) {
        lang = lang || (window.languageManager
            ? window.languageManager.getCurrentLanguage()
            : 'de');

        var src = resolveGrowthSource(chartData);
        if (!src) return null;

        var canvas = document.getElementById('growthEfficiencyChart');
        if (!canvas || typeof Chart === 'undefined') return null;

        if (window.growthEfficiencyChart && typeof window.growthEfficiencyChart.destroy === 'function') {
            window.growthEfficiencyChart.destroy();
            window.growthEfficiencyChart = null;
        }

        var payload = buildGrowthChartPayload(src, chartData, lang);
        if (!payload.datasets.length) return null;

        window.growthEfficiencyChart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: payload.labels,
                datasets: payload.datasets.map(function (ds) {
                    return {
                        label: ds.label,
                        data: ds.values,
                        backgroundColor: ds.color,
                        borderRadius: 4,
                        barPercentage: 0.7,
                        categoryPercentage: 0.65
                    };
                })
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: {
                        display: false,
                        labels: {
                            font: { family: FONT, size: 12 },
                            usePointStyle: true,
                            pointStyleWidth: 14,
                            padding: 20,
                            color: '#424242'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return '  ' + ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(1) + ' %';
                            }
                        },
                        bodyFont: { family: FONT, size: 13 },
                        titleFont: { family: FONT, size: 13, weight: '600' },
                        padding: 10,
                        cornerRadius: 6,
                        boxPadding: 4
                    }
                },
                scales: {
                    y: {
                        min: 0,
                        max: 70,
                        ticks: {
                            callback: function (v) { return v + ' %'; },
                            font: { family: FONT, size: 11 },
                            color: '#9E9E9E',
                            stepSize: 10
                        },
                        grid: { color: '#F2F2F2' },
                        border: { display: false }
                    },
                    x: {
                        ticks: {
                            font: { family: FONT, size: 11, weight: '600' },
                            color: '#424242'
                        },
                        grid: { display: false },
                        border: { display: false }
                    }
                }
            }
        });

        return window.growthEfficiencyChart;
    }

    window.initCompareProductivityChart = initCompareProductivityChart;
    window.initCompareGrowthEfficiencyChart = initCompareGrowthEfficiencyChart;
})();
