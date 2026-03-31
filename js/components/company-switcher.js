/**
 * company-switcher.js
 * Inserts a company <select> and drives all in-place DOM updates for vergleich.html.
 *
 * window.initCompanySwitcher(data)               — insert select, initial render with 'bcg'
 * window.renderComparativePage(data, companyKey) — update all sections in place
 */
(function () {
    'use strict';

    var FONT = "'Open Sans', sans-serif";

    // ── Formatting helpers ────────────────────────────────────────────────────

    function fmt(v) {
        return v.toFixed(1).replace('.', ',');
    }

    function fmtDelta(d) {
        var abs = Math.abs(d);
        var sign = d >= 0 ? '+\u2009' : '\u2212\u2009';
        return sign + fmt(abs) + '\u2009PP';
    }

    function deltaClass(d) {
        if (Math.abs(d) < 0.05) return 'cmp-delta--neu';
        return d > 0 ? 'cmp-delta--pos' : 'cmp-delta--neg';
    }

    function deltaInlineStyle(d) {
        if (Math.abs(d) < 0.05) return 'background:#F5F5F5;color:#616161;';
        return d > 0 ? 'background:#E8F5E9;color:#1B5E20;' : 'background:#FBE9E7;color:#BF360C;';
    }

    // Update a text node inside el (first text-node child), preserving other children.
    function updateTextNode(el, text) {
        if (!el) return;
        for (var i = 0; i < el.childNodes.length; i++) {
            if (el.childNodes[i].nodeType === 3) {
                el.childNodes[i].textContent = text;
                return;
            }
        }
        // No text node found – append one
        el.appendChild(document.createTextNode(text));
    }

    // ── 1. Hero ───────────────────────────────────────────────────────────────

    function updateHero(meta) {
        var el;

        el = document.getElementById('cmp-meta-n-benchmark');
        if (el) el.textContent = meta.n_benchmark;

        el = document.getElementById('cmp-meta-n-company');
        if (el) el.textContent = meta.n_company;

        el = document.getElementById('cmp-meta-company-label');
        if (el) el.textContent = meta.display + ' Teilnehmer';

        el = document.getElementById('cmp-hero-subtitle');
        if (el) el.innerHTML = 'Direkter Vergleich der <strong>' + meta.display
            + '</strong> (n\u00a0=\u00a0' + meta.n_company
            + ') mit dem Gesamtdurchschnitt der 2026-Studie (n\u00a0=\u00a0' + meta.n_benchmark
            + '). Die Auswertung zeigt St\u00e4rken, Abweichungen und strategische Positionierung.';

        // Update all legend labels that carry n values
        document.querySelectorAll('[data-cmp-legend-role="bench"]').forEach(function (el) {
            updateTextNode(el, ' Alle (n=' + meta.n_benchmark + ')');
        });
        document.querySelectorAll('[data-cmp-legend-role="bench-tools"]').forEach(function (el) {
            updateTextNode(el, ' Alle (Nutzer, n=' + meta.n_benchmark_users + ')');
        });
        document.querySelectorAll('[data-cmp-legend-role="company"]').forEach(function (el) {
            updateTextNode(el, ' ' + meta.display + ' (n=' + meta.n_company + ')');
        });
        document.querySelectorAll('[data-cmp-legend-role="company-noN"]').forEach(function (el) {
            updateTextNode(el, ' ' + meta.display);
        });
    }

    // ── 2. KPI cards ──────────────────────────────────────────────────────────

    function updateKPIs(kpis) {
        kpis.forEach(function (kpi) {
            var card = document.querySelector('[data-kpi-id="' + kpi.key + '"]');
            if (!card) return;
            var valEl   = card.querySelector('.kpi-card__value');
            var benchEl = card.querySelector('.kpi-card__bench');
            var deltaEl = card.querySelector('.kpi-card__delta');
            if (valEl)   valEl.textContent   = fmt(kpi.company_value) + '\u2009%';
            if (benchEl) benchEl.textContent = 'Alle: ' + fmt(kpi.bench_value) + '\u2009%';
            if (deltaEl) {
                deltaEl.textContent = fmtDelta(kpi.delta);
                deltaEl.style.cssText = 'display:inline-block;font-size:0.875rem;font-weight:700;padding:0.3rem 0.9rem;border-radius:999px;' + deltaInlineStyle(kpi.delta);
            }
        });
    }

    // ── 3. cmp-rows (generic updater) ─────────────────────────────────────────

    /**
     * Update a single .cmp-row element.
     * barRows[0] = bench row, barRows[1] = company row (always this order in HTML).
     */
    function updateCmpRow(row, companyVal, benchVal, delta, companyName) {
        var deltaEl = row.querySelector('.cmp-delta');
        if (deltaEl) {
            deltaEl.textContent = fmtDelta(delta);
            deltaEl.className = 'cmp-delta ' + deltaClass(delta);
        }
        var barRows = row.querySelectorAll('.cmp-bar-row');
        if (barRows.length >= 2) {
            var benchFill = barRows[0].querySelector('.cmp-bar-row__fill');
            var benchValEl = barRows[0].querySelector('.cmp-bar-row__val');
            if (benchFill)  benchFill.style.width = benchVal + '%';
            if (benchValEl) benchValEl.textContent = fmt(benchVal) + '\u2009%';

            var compFill = barRows[1].querySelector('.cmp-bar-row__fill');
            var compValEl = barRows[1].querySelector('.cmp-bar-row__val');
            var compWho   = barRows[1].querySelector('.cmp-bar-row__who');
            if (compFill)  compFill.style.width = companyVal + '%';
            if (compValEl) compValEl.textContent = fmt(companyVal) + '\u2009%';
            if (compWho && companyName) compWho.textContent = companyName;
        }
    }

    function updateSections(sections, companyName) {
        // usage_frequency
        var ufContainer = document.querySelector('[data-section-container="usage_frequency"]');
        if (ufContainer) {
            ufContainer.querySelectorAll('.cmp-row').forEach(function (row, idx) {
                var item = sections.usage_frequency[idx];
                if (!item) return;
                updateCmpRow(row, item.company_value, item.bench_value, item.company_value - item.bench_value, companyName);
            });
        }

        // tools
        var toolsContainer = document.querySelector('[data-section-container="tools"]');
        if (toolsContainer) {
            toolsContainer.querySelectorAll('.cmp-row').forEach(function (row, idx) {
                var item = sections.tools.items[idx];
                if (!item) return;
                updateCmpRow(row, item.company_value, item.bench_value, item.company_value - item.bench_value, companyName);
            });
        }

        // productivity today
        var ptContainer = document.querySelector('[data-section-container="productivity_today"]');
        if (ptContainer) {
            ptContainer.querySelectorAll('.cmp-row').forEach(function (row, idx) {
                var comp  = sections.productivity.today.items[idx];
                var bench = sections.productivity.today.bench[idx];
                if (!comp || !bench) return;
                updateCmpRow(row, comp.value, bench.value, comp.value - bench.value, companyName);
            });
        }

        // productivity future
        var pfContainer = document.querySelector('[data-section-container="productivity_future"]');
        if (pfContainer) {
            pfContainer.querySelectorAll('.cmp-row').forEach(function (row, idx) {
                var comp  = sections.productivity.future.items[idx];
                var bench = sections.productivity.future.bench[idx];
                if (!comp || !bench) return;
                updateCmpRow(row, comp.value, bench.value, comp.value - bench.value, companyName);
            });
        }

        // privacy
        var privContainer = document.querySelector('[data-section-container="privacy"]');
        if (privContainer) {
            privContainer.querySelectorAll('.cmp-row').forEach(function (row, idx) {
                var item = sections.privacy[idx];
                if (!item) return;
                updateCmpRow(row, item.company_value, item.bench_value, item.company_value - item.bench_value, companyName);
            });
        }

        // growth_efficiency (cmp-rows only, not the chart which is handled separately)
        var geContainer = document.querySelector('[data-section-container="growth_efficiency"]');
        if (geContainer) {
            geContainer.querySelectorAll('.cmp-row').forEach(function (row, idx) {
                var item = sections.growth_efficiency[idx];
                if (!item) return;
                updateCmpRow(row, item.company_value, item.bench_value, item.company_value - item.bench_value, companyName);
            });
        }
    }

    // ── 4. Phase grid ─────────────────────────────────────────────────────────

    function updatePhaseGrid(phaseGrid, meta) {
        ['1', '2', '3', '4'].forEach(function (key, i) {
            var cell = document.querySelector('[data-phase="' + key + '"]');
            var item = phaseGrid[i];
            if (!cell || !item) return;

            var numEl    = cell.querySelector('.phase-num');
            var num2El   = cell.querySelector('.phase-num-2');
            var who2El   = cell.querySelector('.phase-who-2');
            var badgeEl  = cell.querySelector('[data-phase-delta]');

            if (numEl)   numEl.textContent  = fmt(item.bench_value) + '\u2009%';
            if (num2El)  num2El.textContent = fmt(item.company_value) + '\u2009%';
            if (who2El)  who2El.textContent = meta.display;
            if (badgeEl) {
                var d = item.company_value - item.bench_value;
                badgeEl.textContent = fmtDelta(d);
                badgeEl.style.cssText = 'font-size:0.7rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:999px;' + deltaInlineStyle(d);
            }
        });

        // Phase 3+4 summary box
        var p3 = phaseGrid[2], p4 = phaseGrid[3];
        if (p3 && p4) {
            var prodComp  = Math.round((p3.company_value + p4.company_value) * 10) / 10;
            var prodBench = Math.round((p3.bench_value   + p4.bench_value)   * 10) / 10;
            var sumEl = document.getElementById('cmp-phase-summary');
            if (sumEl) sumEl.innerHTML = '<strong>' + fmt(prodComp) + '\u2009% von '
                + meta.display + '</strong> sind bereits in Phase 3 oder 4 (aktiver Produktiveinsatz),'
                + ' verglichen mit <strong>' + fmt(prodBench) + '\u2009%</strong>'
                + ' im Gesamtdurchschnitt \u2014 ein Vorsprung von '
                + fmt(prodComp - prodBench) + ' Prozentpunkten.';
        }
    }

    // ── 5. Challenge ranking ──────────────────────────────────────────────────

    function updateChallengeRanking(challenges, meta) {
        var container = document.getElementById('challenge-ranking');
        if (!container) return;
        var cols     = container.children;
        var leftCol  = cols[0];
        var rightCol = cols[2];

        // Column headers
        var leftHdr  = leftCol  && leftCol.querySelector('[data-rank-header]');
        var rightHdr = rightCol && rightCol.querySelector('[data-rank-header]');
        if (leftHdr)  leftHdr.textContent  = 'Alle (n=' + meta.n_benchmark + ')';
        if (rightHdr) rightHdr.textContent = meta.display + ' (n=' + meta.n_company + ')';

        // Bench items (already ranked in data)
        if (leftCol) {
            leftCol.querySelectorAll('.rank-item[data-cat]').forEach(function (el, i) {
                var entry = challenges.benchmark[i];
                if (!entry) return;
                el.dataset.cat = entry.cat;
                var lbl = el.querySelector('.rank-label');
                var pct = el.querySelector('.rank-pct');
                if (lbl) lbl.textContent = entry.label;
                if (pct) pct.textContent = fmt(entry.value) + '\u2009%';
            });
        }

        // Company items (already ranked in data)
        if (rightCol) {
            rightCol.querySelectorAll('.rank-item[data-cat]').forEach(function (el, i) {
                var entry = challenges.company[i];
                if (!entry) return;
                el.dataset.cat = entry.cat;
                var lbl = el.querySelector('.rank-label');
                var pct = el.querySelector('.rank-pct');
                if (lbl) lbl.textContent = entry.label;
                if (pct) pct.textContent = fmt(entry.value) + '\u2009%';
            });
        }

        // Redraw SVG connectors
        redrawRankConnectors(container);
    }

    function redrawRankConnectors(container) {
        var svg = document.getElementById('rank-connectors');
        if (!svg) return;
        var cols     = container.children;
        var leftCol  = cols[0];
        var svgWrap  = cols[1];
        var rightCol = cols[2];

        var leftItems  = leftCol  ? leftCol.querySelectorAll('.rank-item[data-cat]')  : [];
        var rightItems = rightCol ? rightCol.querySelectorAll('.rank-item[data-cat]') : [];
        if (!leftItems.length) return;

        var rightMap = {};
        rightItems.forEach(function (el) { rightMap[el.dataset.cat] = el; });

        var svgRect = svgWrap.getBoundingClientRect();
        var svgW    = svgRect.width;

        var COLORS = { data:'#1B5E20', roi:'#E65100', it:'#E65100', staff:'#1B5E20', gov:'#E65100' };
        var lines = '';

        leftItems.forEach(function (leftEl) {
            var cat     = leftEl.dataset.cat;
            var rightEl = rightMap[cat];
            if (!rightEl) return;
            var lRect = leftEl.getBoundingClientRect();
            var rRect = rightEl.getBoundingClientRect();
            var y1    = (lRect.top + lRect.height / 2) - svgRect.top;
            var y2    = (rRect.top + rRect.height / 2) - svgRect.top;
            var color = COLORS[cat] || '#9E9E9E';
            var pad   = 10;
            var x1    = pad;
            var x2    = svgW - pad;
            var cpx1  = x1 + (x2 - x1) * 0.35;
            var cpx2  = x1 + (x2 - x1) * 0.65;
            lines += '<path d="M ' + x1 + ' ' + y1 + ' C ' + cpx1 + ' ' + y1 + ', ' + cpx2 + ' ' + y2 + ', ' + x2 + ' ' + y2 + '"'
                   + ' fill="none" stroke="' + color + '" stroke-width="2" stroke-opacity="0.4" stroke-linecap="round" />';
        });

        svg.innerHTML = lines;
    }

    // ── 6. Proficiency bars ───────────────────────────────────────────────────

    function updateProficiency(proficiency) {
        // Compute scale: max height 220 px
        var maxVal = 0;
        proficiency.forEach(function (p) {
            if (p.bench_value   > maxVal) maxVal = p.bench_value;
            if (p.company_value > maxVal) maxVal = p.company_value;
        });
        var scale = maxVal > 0 ? 220 / maxVal : 4;

        proficiency.forEach(function (p, idx) {
            var group = document.querySelector('[data-prof-idx="' + idx + '"]');
            if (!group) return;

            var benchBar  = group.querySelector('[data-prof-bar="bench"]');
            var compBar   = group.querySelector('[data-prof-bar="company"]');
            var benchLbl  = group.querySelector('[data-prof-lbl="bench"]');
            var compLbl   = group.querySelector('[data-prof-lbl="company"]');

            var bh = Math.max(2, Math.round(p.bench_value   * scale));
            var ch = Math.max(2, Math.round(p.company_value * scale));

            if (benchBar)  benchBar.style.height  = bh + 'px';
            if (compBar)   compBar.style.height   = ch + 'px';
            if (benchLbl)  benchLbl.textContent   = fmt(p.bench_value)   + '%';
            if (compLbl)   compLbl.textContent    = fmt(p.company_value) + '%';
        });
    }

    // ── 7. Productivity timeline chart ────────────────────────────────────────

    function updateProductivityChart(cmp) {
        var lang = window.languageManager
            ? window.languageManager.getCurrentLanguage()
            : 'de';

        if (typeof window.initCompareProductivityChart === 'function') {
            window.initCompareProductivityChart(cmp, lang);
        }
    }

    // ── 8. Growth efficiency chart ────────────────────────────────────────────

    function updateGrowthEfficiencyChart(cmp, meta) {
        var lang = window.languageManager
            ? window.languageManager.getCurrentLanguage()
            : 'de';

        if (typeof window.initCompareGrowthEfficiencyChart === 'function') {
            var payload = {
                meta: meta,
                charts: cmp.charts,
                sections: cmp.sections
            };
            window.initCompareGrowthEfficiencyChart(payload, lang);
        }
    }

    // ── 9. Fazit ─────────────────────────────────────────────────────────────

    function updateFazit(fazit, lang) {
        var el = document.querySelector('[data-fazit]');
        if (!el) return;

        var preferred = lang === 'en' ? 'en' : 'de';
        var fallback  = preferred === 'en' ? 'de' : 'en';
        var text = (fazit && fazit[preferred]) ? fazit[preferred]
            : (fazit && fazit[fallback]) ? fazit[fallback]
            : null;

        if (text) {
            el.innerHTML = text;
        } else {
            el.innerHTML = '<em>Die detaillierte Einordnung f\u00fcr dieses Unternehmen wird in K\u00fcrze erg\u00e4nzt. '
                + 'Bei Fragen wenden Sie sich direkt an <a href="mailto:ai-survey@th-brandenburg.de">ai-survey@th-brandenburg.de</a>.</em>';
        }
    }

    // ── 10. PDF meta ─────────────────────────────────────────────────────────

    function updatePDFMeta(name, n) {
        if (typeof initPDFExport === 'function') {
            initPDFExport({
                filename: 'Unternehmensvergleich_' + name.replace(/\s+/g, '_') + '_2026.pdf',
                title: 'Unternehmensvergleich 2026',
                subtitle: name + ' (n\u00a0=\u00a0' + n + ') vs. Gesamtdurchschnitt (n\u00a0=\u00a0346)',
                meta: 'Firmenspezifischer Vergleich \u00b7 2026',
                _loadingText: 'PDF wird erstellt\u2026'
            });
        }
    }

    // ── Main render ──────────────────────────────────────────────────────────

    function renderComparativePage(data, companyKey) {
        var cmp = data.comparative[companyKey];
        if (!cmp) { console.warn('[company-switcher] Unknown key:', companyKey); return; }
        var lang = window.languageManager
            ? window.languageManager.getCurrentLanguage()
            : 'de';

        var meta     = cmp.meta;
        var sections = cmp.sections;

        updateHero(meta);
        updateKPIs(cmp.kpis);
        updateSections(sections, meta.display);
        updatePhaseGrid(sections.phase_grid, meta);
        updateChallengeRanking(sections.challenges_rank, meta);
        updateProficiency(sections.proficiency);
        updateProductivityChart(cmp);
        updateGrowthEfficiencyChart(cmp, meta);
        updateFazit(cmp.fazit, lang);
        updatePDFMeta(meta.display, meta.n_company);
    }

    // ── Init: insert <select> and render default ──────────────────────────────

    function initCompanySwitcher(data) {
        var placeholder = document.getElementById('company-switcher-placeholder');
        if (!placeholder) {
            console.warn('[company-switcher] #company-switcher-placeholder not found');
            return;
        }

        var wrapper = document.createElement('div');
        wrapper.style.cssText = 'display:flex;align-items:center;gap:0.75rem;justify-content:center;margin-bottom:1.5rem;';

        var label = document.createElement('label');
        label.textContent = 'Unternehmen:';
        label.style.cssText = 'font-size:0.875rem;font-weight:600;color:var(--th-gray);';

        var select = document.createElement('select');
        select.id = 'company-select';
        select.style.cssText = 'font-size:0.9375rem;font-weight:600;color:var(--th-blue);background:white;'
            + 'border:2px solid var(--th-blue);border-radius:0.5rem;padding:0.4rem 1rem;cursor:pointer;min-width:14rem;';

        Object.keys(data.comparative).forEach(function (key) {
            var meta = data.comparative[key].meta;
            var opt  = document.createElement('option');
            opt.value       = key;
            opt.textContent = meta.display;
            select.appendChild(opt);
        });

        select.value = 'bcg';
        select.addEventListener('change', function () {
            renderComparativePage(data, this.value);
        });

        wrapper.appendChild(label);
        wrapper.appendChild(select);
        placeholder.appendChild(wrapper);

        // Initial render with BCG data (matches the static HTML skeleton)
        renderComparativePage(data, 'bcg');
    }

    // Public API
    window.initCompanySwitcher   = initCompanySwitcher;
    window.renderComparativePage = renderComparativePage;

})();

export const initCompanySwitcher = window.initCompanySwitcher;
export const renderComparativePage = window.renderComparativePage;
