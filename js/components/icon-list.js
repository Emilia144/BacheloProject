/**
 * icon-list.js — Reusable icon-list component (dashboard cards).
 *
 * Renders a vertical list of icon + label + value rows using the
 * existing .icon-list / .icon-list__item CSS classes.
 *
 * @param {string}   containerId  Target element id
 * @param {Object[]} items        Array of row descriptors
 *   - icon       {string}  Lucide icon name (e.g. 'git-merge')
 *   - label_i18n {string}  i18n key
 *   - value      {string}  Display string (e.g. '45%')
 *   - highlight  {boolean} If true, applies accent background + border
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

    function renderIconList(containerId, items, options) {
        options = options || {};
        var container = document.getElementById(containerId);
        if (!container || !items) return;

        var lang = options.lang || (window.languageManager
            ? window.languageManager.getCurrentLanguage() : 'de');

        var parts = ['<div class="icon-list">'];

        items.forEach(function (item) {
            var label = t(item.label_i18n, lang, item.label_i18n);
            var hlStyle = item.highlight
                ? ' style="background:var(--accent-muted); border:1px solid var(--accent-light);"'
                : '';

            parts.push(
                '<div class="icon-list__item"' + hlStyle + '>'
                + '<div class="icon-list__icon">'
                +   '<i data-lucide="' + esc(item.icon) + '" style="width:1.5rem;height:1.5rem;color:var(--th-blue);"></i>'
                + '</div>'
                + '<div class="icon-list__content">'
                +   '<div class="icon-list__title" style="display:flex;justify-content:space-between;align-items:center">'
                +     '<span data-i18n="' + esc(item.label_i18n) + '">' + esc(label) + '</span>'
                +     '<strong>' + esc(String(item.value)) + '</strong>'
                +   '</div>'
                + '</div>'
                + '</div>'
            );
        });

        parts.push('</div>');
        container.innerHTML = parts.join('');

        // Re-initialize lucide icons inside the new content
        if (window.lucide && window.lucide.createIcons) {
            window.lucide.createIcons({ nodes: [container] });
        }
    }

    window.renderIconList = renderIconList;
})();
