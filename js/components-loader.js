/**
 * TH Brandenburg - Component Loader
 * Lädt Header und Footer dynamisch in alle Seiten
 */

// Funktion zum Laden von HTML-Komponenten
async function loadComponent(elementId, componentPath) {
    try {
        const response = await fetch(componentPath);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const html = await response.text();
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = html;
            return true;
        }
        return false;
    } catch (error) {
        console.error(`Fehler beim Laden von ${componentPath}:`, error);
        return false;
    }
}

// Funktion zum Markieren der aktiven Navigation
function highlightActiveNav() {
    // Aktuellen Seitennamen und Hash ermitteln
    const currentPath = window.location.pathname;
    const currentPage = currentPath.split('/').pop() || 'index.html';
    const currentHash = window.location.hash;
    
    // Alle Navigationslinks durchgehen
    const navLinks = document.querySelectorAll('.header__nav a');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        const linkPage = link.getAttribute('data-page') || href.split('#')[0];
        const linkHash = href.includes('#') ? '#' + href.split('#')[1] : '';
        
        let isActive = false;
        
        // Prüfen ob Link aktiv ist
        if (linkPage !== currentPage) {
            // Andere Seite - nicht aktiv
            isActive = false;
        } else if (linkHash && currentHash) {
            // Beide haben Hash - müssen übereinstimmen
            isActive = linkHash === currentHash;
        } else if (linkHash && !currentHash) {
            // Link hat Hash, Seite nicht - nicht aktiv
            isActive = false;
        } else if (!linkHash && currentHash) {
            // Link hat keinen Hash, Seite schon - nicht aktiv
            isActive = false;
        } else {
            // Beide haben keinen Hash - aktiv wenn gleiche Seite
            isActive = true;
        }
        
        // CSS-Klasse entsprechend setzen
        if (isActive) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Hauptfunktion zum Initialisieren der Komponenten
async function initComponents() {
    // Loading-Indikator anzeigen (optional)
    document.body.classList.add('components-loading');
    
    // Header und Footer parallel laden
    const [headerLoaded, footerLoaded] = await Promise.all([
        loadComponent('header-placeholder', 'header.html'),
        loadComponent('footer-placeholder', 'footer.html')
    ]);
    
    // Loading-Indikator entfernen
    document.body.classList.remove('components-loading');
    
    // Wenn Header geladen wurde, aktive Navigation markieren
    if (headerLoaded) {
        highlightActiveNav();
        
        // Event Listener für Hash-Änderungen (für Single-Page-Navigation)
        window.addEventListener('hashchange', highlightActiveNav);
        
        // Custom Event für Header-Laden feuern (für i18n und andere Module)
        window.dispatchEvent(new CustomEvent('headerLoaded'));
    }
    
    // Lucide Icons initialisieren (falls verfügbar)
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
        lucide.createIcons();
    }
    
    // Fehlerbehandlung
    if (!headerLoaded) {
        console.warn('Header konnte nicht geladen werden. Bitte prüfen Sie, ob header.html existiert und über einen Webserver bereitgestellt wird.');
    }
    if (!footerLoaded) {
        console.warn('Footer konnte nicht geladen werden. Bitte prüfen Sie, ob footer.html existiert und über einen Webserver bereitgestellt wird.');
    }
}

// Komponenten laden, sobald das DOM bereit ist
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initComponents);
} else {
    // DOM ist bereits geladen
    initComponents();
}
