# KI im IT-Arbeitsalltag 2026 | TH Brandenburg Dashboard

## Überblick
Vollständige Website mit Dashboard zur Analyse des Einsatzes von GenAI-Tools in der deutschen IT-Branche, entwickelt für die Technische Hochschule Brandenburg.

### Seiten
1. **index.html** - Startseite mit Projektübersicht, aktuellen Umfragen und Call-to-Action
2. **ergebnisse-2024.html** - Detaillierte Ergebnisse der Studie 2024 mit Visualisierungen
3. **ai-survey-2026.html** - Interaktives Dashboard 2026 mit Unternehmensvergleich

## Design-Integration

### TH Brandenburg Corporate Design Elemente

Das Dashboard wurde mit den wesentlichen Designelementen der TH Brandenburg integriert, während die ursprüngliche Dashboard-Funktionalität vollständig erhalten bleibt.

#### Farbschema
- **Primärfarbe (TH Blau)**: `#004A99` - Hauptidentitätsfarbe der TH Brandenburg
- **Sekundärfarben**: 
  - Helles Blau: `#0066CC`
  - Dunkles Blau: `#003366`
- **Akzentfarbe (TH Rot)**: `#E30613` - Für Hervorhebungen und Vergleiche
- **Grautöne**: Professionelle, neutrale Farben für Text und Hintergründe

#### Typografie
- **Display-Schrift**: Roboto Slab - Für Überschriften und wichtige Zahlen
- **Body-Schrift**: Open Sans - Für Fließtext und Beschreibungen
- **Monospace**: Roboto Mono - Für Daten und Code-Elemente

### Wiederverwendbare Komponenten

**Header und Footer sind in separate Dateien ausgelagert:**

- **header.html** - Enthält die komplette Header-Struktur mit Navigation
- **footer.html** - Enthält die komplette Footer-Struktur
- **components-loader.js** - JavaScript, das beide Komponenten dynamisch lädt

**Vorteile:**
- ✅ **Zentrale Wartung**: Header/Footer nur einmal bearbeiten
- ✅ **Automatische Updates**: Änderungen erscheinen sofort auf allen Seiten
- ✅ **Aktive Navigation**: Wird automatisch basierend auf der aktuellen Seite markiert
- ✅ **DRY-Prinzip**: Kein doppelter Code mehr

**Header/Footer ändern:**
1. Öffnen Sie `header.html` oder `footer.html`
2. Nehmen Sie Ihre Änderungen vor
3. Speichern - fertig! Alle Seiten nutzen die aktualisierte Version

### Navigation zwischen den Seiten

Alle drei Seiten sind vollständig miteinander verlinkt:

- **Header-Navigation**: Konsistente Navigation auf allen Seiten mit Links zu:
  - Startseite (index.html)
  - Ergebnisse 2024 (ergebnisse-2024.html)
  - Dashboard 2026 (KI im IT-Arbeitsalltag 2025 _ TH Brandenburg.htm)
  
- **Call-to-Action Buttons**: Strategisch platzierte Buttons für:
  - Teilnahme an Umfrage 2026
  - Wechsel zwischen den verschiedenen Ansichten
  
- **Footer-Links**: Zusätzliche Navigation im Footer jeder Seite

### Hauptmerkmale

#### 1. Header (TH Brandenburg Branding)
- Dreifarbiger Rahmen unten (TH Brandenburg Blau)
- Vergrößertes Logo-Icon mit TH Brandenburg Farben
- Professionelle Navigation mit Hover-Effekten
- Responsive Design für alle Bildschirmgrößen

#### 2. Hero-Bereich
- Gradient-Hintergrund für visuelle Tiefe
- TH Brandenburg Badge mit pulsierender Animation
- Großzügige, klare Typografie
- Prominente Darstellung der Key-Metriken

#### 3. Karten und Visualisierungen
- Moderne Schatten-Effekte
- TH Brandenburg Farbschema in allen Charts
- Hover-Animationen für bessere Interaktivität
- Konsistente Border-Radius (`4px` - TH Brandenburg Standard)

#### 4. Footer
- Dunkelblaue Hintergrundfarbe (TH Brandenburg Blau)
- Weiße Schrift für hohen Kontrast
- Klare Struktur mit Links und Copyright-Informationen

### Technische Details

#### Dateistruktur
```
Dashboard/
├── index.html                                         # Startseite / Projektübersicht
├── ergebnisse-2024.html                               # Ergebnisse Studie 2024
├── KI im IT-Arbeitsalltag 2025 _ TH Brandenburg.htm  # Dashboard 2026
├── header.html                                        # ⭐ Wiederverwendbarer Header
├── footer.html                                        # ⭐ Wiederverwendbarer Footer
├── components-loader.js                               # ⭐ JavaScript zum dynamischen Laden
├── styles.css                                         # Konsolidiertes CSS (genutzt von allen Seiten)
├── KI im IT-Arbeitsalltag 2025 _ TH Brandenburg-Dateien/
│   └── css2.css                                       # Google Fonts Definitionen
├── README.md                                          # Diese Dokumentation
└── WEBSERVER-ANLEITUNG.md                             # ⭐ Anleitung zum lokalen Webserver
```

**⭐ Neu:** Header und Footer sind jetzt in separate Dateien ausgelagert und werden dynamisch geladen.

#### CSS-Variablen (Design-System)
Alle TH Brandenburg Farben und Styles sind als CSS-Variablen definiert:

```css
:root {
  --th-blue: #004A99;
  --th-blue-light: #0066CC;
  --th-blue-dark: #003366;
  --th-accent: #E30613;
  --th-gray: #4A4A4A;
  /* ... weitere Variablen */
}
```

#### Responsive Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Komponenten

#### Visualisierungen
1. **Bar-Charts**: Horizontale Balkendiagramme mit TH Blau-Gradient
2. **Donut-Charts**: Kreisdiagramme mit TH Brandenburg Farbpalette
3. **Stats-Grid**: Responsive Zahlen-Kacheln
4. **Matrix-Charts**: Kompakte Listen-Darstellung
5. **Comparison-View**: Unternehmensvergleiche mit dualer Farbgebung

#### Interaktive Elemente
- **View-Toggle**: Wechsel zwischen Gesamt- und Vergleichsansicht
- **Company-Selector**: Dropdown zur Unternehmensauswahl
- **Navigation**: Smooth-Scroll zu Dashboard-Sektionen
- **Hover-Effekte**: Visuelles Feedback bei allen interaktiven Elementen

### Accessibility (Barrierefreiheit)

- **Keyboard-Navigation**: Vollständig tastaturzugänglich
- **Focus-Indicators**: Sichtbare Focus-Zustände (2px TH Blau)
- **Farbkontraste**: WCAG AA konform
- **Semantisches HTML**: Korrekte Verwendung von Header, Nav, Section, Footer
- **Screen-Reader freundlich**: Alt-Texte und ARIA-Labels wo nötig

### Performance-Optimierungen

1. **CSS-Konsolidierung**: Alle Styles in einer Datei
2. **Google Fonts**: Preconnect für schnellere Ladezeiten
3. **Smooth Animations**: Hardware-beschleunigte Transformationen
4. **Optimierte Schatten**: Reduzierte Blur-Werte für bessere Performance

### Browser-Kompatibilität

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Opera 76+

### Anpassungen & Wartung

#### Farben ändern
Bearbeiten Sie die CSS-Variablen in `styles.css` (Zeilen 2-40):

```css
:root {
  --th-blue: #004A99;  /* Ihre Primärfarbe */
  --th-accent: #E30613; /* Ihre Akzentfarbe */
}
```

#### Schriftarten ändern
Aktualisieren Sie den Google Fonts Link im HTML und die CSS-Variablen:

```html
<link href="https://fonts.googleapis.com/css2?family=Ihre+Schrift&display=swap" rel="stylesheet">
```

```css
:root {
  --font-body: "Ihre Schrift", system-ui, sans-serif;
}
```

## Verwendung

### ⚠️ Wichtig: Webserver erforderlich!

**Seit der Auslagerung von Header und Footer wird ein Webserver benötigt!**

Die Website verwendet JavaScript `fetch()` zum dynamischen Laden von Komponenten. Dies funktioniert **nicht** mit dem `file://` Protokoll.

**Schnellstart mit Python:**
```bash
# Im Projekt-Verzeichnis ausführen:
python -m http.server 8000

# Dann im Browser öffnen:
# http://localhost:8000
```

**Weitere Optionen** (Node.js, PHP, VS Code Live Server) finden Sie in der **WEBSERVER-ANLEITUNG.md**.

### Lokale Ansicht
Verwenden Sie einen lokalen Webserver (siehe oben). Alle Links und Funktionen funktionieren dann einwandfrei.

### Hosting
Laden Sie alle Dateien auf einen Webserver hoch und stellen Sie sicher, dass:
- Alle HTML-Dateien im gleichen Verzeichnis liegen
- Die `styles.css` im gleichen Verzeichnis liegt
- Die Google Fonts geladen werden können (Internet-Verbindung erforderlich)

### Anpassungen vornehmen
1. **Farben ändern**: Bearbeiten Sie die CSS-Variablen in `styles.css` (Zeilen 2-40)
2. **Inhalte aktualisieren**: Ändern Sie die HTML-Dateien direkt
3. **Neue Daten**: Passen Sie die JavaScript-Daten im Dashboard an (ab Zeile 444 in der Dashboard-Datei)

## Datenschutz & Nutzung

Diese Website wurde für die **Technische Hochschule Brandenburg** entwickelt.
© 2024-2026 Technische Hochschule Brandenburg

## Kontakt

Bei Fragen oder Anpassungswünschen wenden Sie sich bitte an die IT-Abteilung der TH Brandenburg.

---

**Version**: 1.0  
**Letzte Aktualisierung**: Januar 2026  
**Status**: Produktionsbereit ✅
