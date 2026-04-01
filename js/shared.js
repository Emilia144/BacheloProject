/**
 * shared.js — Foundation module for all Chart.js pages.
 *
 * Provides:
 *   Shared.loadData(url?)          – fetch JSON, cache as window.DATA
 *   Shared.registerChart(id, inst) – track a Chart.js instance
 *   Shared.destroyAll()            – destroy every registered chart
 *   Shared.getChart(id)            – retrieve a registered instance
 *   Shared.onLanguageChange(fn)    – wire languageChanged → destroyAll + fn(DATA, lang)
 *   Shared.baseLineOptions(o)      – base options for line charts
 *   Shared.baseStackedBarOptions(o)– base options for stacked bar charts
 *   Shared.renderCombinedLine(id, chartData) – create & register a line chart
 *   Shared.renderStackedBar(id, chartData)   – create & register a stacked bar chart
 *   Shared.createStripedPattern(fg, bg)      – diagonal hatch canvas pattern
 *   Shared.normalize(raw)                    – row-wise % normalization
 *   Shared.FONT                              – shared font-family string
 */
(function () {
    'use strict';

    // ───────────────────────────────────────────────────
    //  Constants (extracted from existing inline styles)
    // ───────────────────────────────────────────────────
    var FONT = "'Open Sans', sans-serif";

    // ───────────────────────────────────────────────────
    //  Data loader
    // ───────────────────────────────────────────────────
    var _dataPromise = null;

    function loadData(url) {
        url = url || 'data/data.json';
        if (!_dataPromise) {
            _dataPromise = fetch(url)
                .then(function (r) {
                    if (!r.ok) throw new Error('Failed to load ' + url + ' (' + r.status + ')');
                    return r.json();
                })
                .then(function (data) {
                    window.DATA = data;
                    return data;
                })
                .catch(function (err) {
                    console.warn('[shared.js] loadData:', err.message);
                    window.DATA = null;
                    _dataPromise = null;   // allow retry
                    return null;
                });
        }
        return _dataPromise;
    }

    // ───────────────────────────────────────────────────
    //  Chart registry
    // ───────────────────────────────────────────────────
    var _charts = {};

    function registerChart(id, instance) {
        if (_charts[id]) {
            _charts[id].destroy();
        }
        _charts[id] = instance;
    }

    function destroyAll() {
        Object.keys(_charts).forEach(function (id) {
            if (_charts[id]) {
                _charts[id].destroy();
            }
        });
        _charts = {};
    }

    function getChart(id) {
        return _charts[id] || null;
    }

    // ───────────────────────────────────────────────────
    //  Language-change wiring
    // ───────────────────────────────────────────────────
    function onLanguageChange(rerenderFn) {
        document.addEventListener('languageChanged', function (e) {
            destroyAll();
            rerenderFn(window.DATA, e.detail.lang);
        });
    }

    // ───────────────────────────────────────────────────
    //  Base Chart.js option builders
    // ───────────────────────────────────────────────────

    /**
     * Base options for line charts.
     * Matches: productivityChart, challengesChart, growthEfficiencyChart.
     *
     * @param {Object} [overrides]
     * @param {number} [overrides.yMax=100]
     * @param {number} [overrides.yStepSize=20]
     */
    function baseLineOptions(overrides) {
        overrides = overrides || {};
        return {
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
                    max: overrides.yMax || 100,
                    ticks: {
                        callback: function (v) { return v + ' %'; },
                        font: { family: FONT, size: 11 },
                        color: '#BEBEBE',
                        stepSize: overrides.yStepSize || 20
                    },
                    grid: { color: '#F2F2F2' },
                    border: { display: false }
                },
                x: {
                    ticks: {
                        font: { family: FONT, size: 12, weight: '600' },
                        color: '#424242'
                    },
                    grid: { display: false },
                    border: { display: false }
                }
            }
        };
    }

    /**
     * Base options for 100%-stacked bar charts.
     * Matches: stackedTodayChart, stackedFutureChart, growthEfficiencyProficiencyChart.
     *
     * @param {Object} [overrides]
     * @param {number} [overrides.yMax=100]
     * @param {number} [overrides.yStepSize=25]
     */
    function baseStackedBarOptions(overrides) {
        overrides = overrides || {};
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    display: false,
                    labels: {
                        font: { family: FONT, size: 11 },
                        usePointStyle: true,
                        pointStyle: 'rectRounded',
                        padding: 14,
                        color: '#424242'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            var raw = ctx.dataset.rawCounts
                                ? ctx.dataset.rawCounts[ctx.dataIndex]
                                : null;
                            var suffix = raw != null ? ' (n=' + raw + ')' : '';
                            return '  ' + ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(1) + ' %' + suffix;
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
                x: {
                    stacked: true,
                    ticks: {
                        font: { family: FONT, size: 10 },
                        color: '#424242',
                        maxRotation: 0
                    },
                    grid: { display: false },
                    border: { display: false }
                },
                y: {
                    stacked: true,
                    min: 0,
                    max: overrides.yMax || 100,
                    ticks: {
                        callback: function (v) { return v + '%'; },
                        font: { family: FONT, size: 10 },
                        color: '#BEBEBE',
                        stepSize: overrides.yStepSize || 25
                    },
                    grid: { color: 'rgba(0,0,0,0.06)' },
                    border: { display: false }
                }
            }
        };
    }

    // ───────────────────────────────────────────────────
    //  Renderer: combined line chart
    // ───────────────────────────────────────────────────

    /**
     * Create a line chart matching the existing style and register it.
     *
     * @param {string} id            Canvas element id
     * @param {Object} chartData
     * @param {string[]}       chartData.labels         X-axis labels
     * @param {Object[]}       chartData.datasets       Array of dataset descriptors
     *   Required per dataset: label, data, borderColor
     *   Optional overrides:   borderWidth, borderDash, pointRadius, pointHoverRadius,
     *                         pointBackgroundColor, backgroundColor, tension, fill, order
     * @param {number}         [chartData.yMax=100]     Y-axis maximum
     * @param {number}         [chartData.yStepSize=20] Y-axis step size
     * @param {Function}       [chartData.tooltipLabel] Custom tooltip label callback
     * @param {Object[]}       [chartData.plugins]      Chart.js plugins array (e.g. forecastBgPlugin)
     * @returns {Chart|null}
     */
    function renderCombinedLine(id, chartData) {
        var canvas = document.getElementById(id);
        if (!canvas || typeof Chart === 'undefined') return null;

        // Apply per-dataset defaults that match the existing inline style
        var datasets = chartData.datasets.map(function (ds) {
            return Object.assign(
                {
                    borderWidth: 2.5,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: ds.borderColor,
                    tension: 0.35,
                    fill: false
                },
                ds
            );
        });

        var options = baseLineOptions({
            yMax: chartData.yMax,
            yStepSize: chartData.yStepSize
        });

        if (chartData.tooltipLabel) {
            options.plugins.tooltip.callbacks.label = chartData.tooltipLabel;
        }

        var config = {
            type: 'line',
            data: { labels: chartData.labels, datasets: datasets },
            options: options
        };

        if (chartData.plugins) {
            config.plugins = chartData.plugins;
        }

        var instance = new Chart(canvas, config);
        registerChart(id, instance);
        return instance;
    }

    // ───────────────────────────────────────────────────
    //  Renderer: 100%-stacked bar chart
    // ───────────────────────────────────────────────────

    /**
     * Create a stacked bar chart matching the existing style and register it.
     *
     * @param {string} id            Canvas element id
     * @param {Object} chartData
     * @param {string[]}       chartData.labels         X-axis category labels
     * @param {Object[]}       chartData.datasets       Array of dataset descriptors
     *   Required per dataset: label, data, backgroundColor
     *   Optional:             rawCounts (int[]), borderColor, borderWidth, borderRadius
     * @param {Object}         [chartData.axisTitles]   { x: string, y: string }
     * @param {number}         [chartData.yMax=100]     Y-axis maximum
     * @param {number}         [chartData.yStepSize=25] Y-axis step size
     * @param {Function}       [chartData.tooltipLabel] Custom tooltip label callback
     * @returns {Chart|null}
     */
    function renderStackedBar(id, chartData) {
        var canvas = document.getElementById(id);
        if (!canvas || typeof Chart === 'undefined') return null;

        // Apply per-dataset defaults that match the existing inline style
        var datasets = chartData.datasets.map(function (ds) {
            return Object.assign(
                {
                    borderColor: '#fff',
                    borderWidth: 1,
                    borderRadius: 2
                },
                ds
            );
        });

        var options = baseStackedBarOptions({
            yMax: chartData.yMax,
            yStepSize: chartData.yStepSize
        });

        // Axis titles (used by proficiency × productivity and proficiency × growth charts)
        if (chartData.axisTitles) {
            if (chartData.axisTitles.x) {
                options.scales.x.title = {
                    display: true,
                    text: chartData.axisTitles.x,
                    font: { size: 12, weight: 600 },
                    color: '#374151'
                };
            }
            if (chartData.axisTitles.y) {
                options.scales.y.title = {
                    display: true,
                    text: chartData.axisTitles.y,
                    font: { size: 12, weight: 600 },
                    color: '#374151'
                };
            }
        }

        if (chartData.tooltipLabel) {
            options.plugins.tooltip.callbacks.label = chartData.tooltipLabel;
        }

        var instance = new Chart(canvas, {
            type: 'bar',
            data: { labels: chartData.labels, datasets: datasets },
            options: options
        });
        registerChart(id, instance);
        return instance;
    }

    // ───────────────────────────────────────────────────
    //  Utilities
    // ───────────────────────────────────────────────────

    /**
     * Create diagonal striped canvas pattern.
     * Matches the existing "both equally" hatch used in growth/efficiency charts.
     *
     * @param {string} fg  Foreground stripe color (default '#004A99')
     * @param {string} bg  Background fill color  (default '#90CAF9')
     * @returns {CanvasPattern}
     */
    function createStripedPattern(fg, bg) {
        fg = fg || '#004A99';
        bg = bg || '#90CAF9';
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

    /**
     * Row-wise normalization: convert raw count rows to percentages.
     * Matches the existing normalize() used by stacked proficiency charts.
     *
     * @param {number[][]} raw  Array of rows, each row is an array of counts
     * @returns {number[][]}    Same shape, values as percentages (1 decimal)
     */
    function normalize(raw) {
        return raw.map(function (row) {
            var total = row.reduce(function (a, b) { return a + b; }, 0);
            if (total === 0) return row.map(function () { return 0; });
            return row.map(function (v) { return Math.round(v / total * 1000) / 10; });
        });
    }

    // ───────────────────────────────────────────────────
    //  Public API
    // ───────────────────────────────────────────────────
    window.Shared = {
        FONT: FONT,
        loadData: loadData,
        registerChart: registerChart,
        destroyAll: destroyAll,
        getChart: getChart,
        onLanguageChange: onLanguageChange,
        baseLineOptions: baseLineOptions,
        baseStackedBarOptions: baseStackedBarOptions,
        renderCombinedLine: renderCombinedLine,
        renderStackedBar: renderStackedBar,
        createStripedPattern: createStripedPattern,
        normalize: normalize
    };
})();
