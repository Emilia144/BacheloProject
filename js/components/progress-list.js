/**
 * progress-list.js — Reusable progress-bar list component.
 *
 * Renders a vertical list of labelled progress bars into a container.
 *
 * @param {string} containerId   Target element id
 * @param {Object[]} items       Array of bar descriptors
 *   - label_i18n  {string}  i18n key (also used as data-i18n attr)
 *   - value       {number}  0-100, drives bar width
 *   - color       {string?} CSS background for bar fill
 *   - valueColor  {string?} CSS color for the value text
 *   - labelColor  {string?} CSS color for the label text
 *   - labelWeight {string?} CSS font-weight for the label (default '500')
 *   - displayValue{string?} Custom value text (default: value+'%')
 * @param {Object}   [options]
 *   - primaryColor {string}  Default bar + value color (default 'var(--th-blue)')
 *   - trackColor   {string}  Track background (default '#E0E0E0')
 *   - insightKey   {string?} i18n key → renders insight box below the list
 *   - insightHtml  {string?} Default HTML for the insight box (German)
 *   - lang         {string}  Current language code
 */
(function () {
    'use strict';

    function t(key, lang, fallback) {
        if (window.languageManager && window.languageManager.getTranslation) {
            return window.languageManager.getTranslation(key, lang);
        }
        return fallback || key;
    }

    function esc(s) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(s));
        return d.innerHTML;
    }

    function renderProgressList(containerId, items, options) {
        options = options || {};
        var container = document.getElementById(containerId);
        if (!container || !items) return;

        var primary    = options.primaryColor || 'var(--th-blue)';
        var trackColor = options.trackColor   || '#E0E0E0';
        var lang       = options.lang || (window.languageManager
            ? window.languageManager.getCurrentLanguage() : 'de');

        var parts = ['<div style="display:flex;flex-direction:column;gap:1rem;">'];

        items.forEach(function (item) {
            var label       = t(item.label_i18n, lang, item.label_i18n);
            var barColor    = item.color      || primary;
            var valueColor  = item.valueColor || (item.color ? '' : primary);
            var labelColor  = item.labelColor || '';
            var labelWeight = item.labelWeight || '500';
            var display     = item.displayValue != null ? item.displayValue : (item.value + '%');

            var valStyle = valueColor ? ' style="color:' + valueColor + ';"' : '';
            var lblStyle = 'font-weight:' + labelWeight + ';'
                + (labelColor ? 'color:' + labelColor + ';' : '');

            parts.push(
                '<div>'
                + '<div style="display:flex;justify-content:space-between;margin-bottom:0.25rem;padding:0 0.25rem;">'
                +   '<span style="' + lblStyle + '" data-i18n="' + esc(item.label_i18n) + '">' + esc(label) + '</span>'
                +   '<strong' + valStyle + '>' + esc(String(display)) + '</strong>'
                + '</div>'
                + '<div style="width:100%;height:8px;background:' + trackColor + ';border-radius:4px;overflow:hidden;">'
                +   '<div style="width:' + item.value + '%;height:100%;background:' + barColor + ';border-radius:4px;"></div>'
                + '</div>'
                + '</div>'
            );
        });

        parts.push('</div>');

        if (options.insightKey) {
            var insightText = options.insightHtml
                || t(options.insightKey, lang, '');
            parts.push(
                '<p style="margin:1rem 0 0 0;padding:1rem;background:#EEF5FF;border-radius:0.375rem;'
                + 'color:var(--th-gray);line-height:1.6;" data-i18n="' + esc(options.insightKey)
                + '" data-i18n-html="true">' + insightText + '</p>'
            );
        }

        container.innerHTML = parts.join('');
    }

    window.renderProgressList = renderProgressList;
})();
