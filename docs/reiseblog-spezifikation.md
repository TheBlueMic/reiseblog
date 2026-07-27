# Spezifikation: Statischer Reiseblog (USA-Reise Aug 2026)

## Ziel
Ein einfacher, statischer Reiseblog, den man ohne Server/Datenbank betreiben kann. Hosting über GitHub Pages oder Netlify (kostenlos). Unterwegs sollen neue Einträge (Text + Fotos) möglichst einfach hinzugefügt werden können – idealerweise durch Hochladen einer neuen Datei ins Repository, ohne Programmierkenntnisse.

## Technologie
- Reines **HTML + CSS**, kein JavaScript-Framework nötig
- Blog-Einträge als einzelne **Markdown-Dateien** (z. B. `posts/2026-08-11-grand-canyon.md`), die über ein einfaches Build-Skript zu HTML-Seiten werden
  - Alternative, falls einfacher: direkt fertige HTML-Dateien pro Eintrag, ohne Umwandlung – dann entfällt der Build-Schritt komplett
- Kein Datenbank-Server, keine Login-Funktion, keine Kommentarfunktion (Version 1)

## Seitenstruktur

### Startseite (`index.html`)
- Kurzer Titel/Intro zur Reise (z. B. "USA Roadtrip 2026")
- Chronologische Liste aller Blogeinträge (neuester zuerst), je mit:
  - Titel
  - Datum
  - Kurzer Teaser-Text (1–2 Sätze)
  - Vorschaubild (falls vorhanden)
  - Link zum vollständigen Eintrag

### Einzelner Blogeintrag (`posts/<datum>-<titel>.html`)
- Titel
- Datum
- Fließtext
- Eingebettete Fotos (responsive, damit sie auf dem Handy gut aussehen)
- Zurück-Link zur Startseite

### Über-die-Reise-Seite (optional, `about.html`)
- Kurzinfo zur Route, z. B. Karte oder Liste der Stationen (Las Vegas → Grand Canyon → Barstow → Sequoia → Yosemite → Pismo Beach → Hearst Castle → Big Sur → Santa Cruz → San Francisco)

## Design
- Schlicht, mobilfreundlich (responsive), gut lesbar auf dem Handy-Bildschirm
- Foto-Galerien: einfaches CSS-Grid, keine komplexen Lightbox-Bibliotheken nötig (Version 1)
- Farbschema und Schriftart: einfache, angenehme Defaults (z. B. serifenlose Schrift, viel Weißraum) – kann später gerne individueller werden

## SEO / Auffindbarkeit (wie besprochen)

### Meta-Tags (in jeder Seite)
- `<title>` pro Seite individuell (z. B. "Grand Canyon – USA Roadtrip 2026")
- `<meta name="description" content="...">` – kurze Beschreibung pro Seite
- Open-Graph-Tags (`og:title`, `og:description`, `og:image`) für schönere Vorschau beim Teilen in WhatsApp/Social Media

### Sitemap
- Automatisch generierte `sitemap.xml`, die alle Seiten auflistet (aktualisiert sich bei jedem neuen Post, wenn ein Build-Skript verwendet wird)

### robots.txt
- Einfache `robots.txt`, die Suchmaschinen erlaubt, die Seite zu crawlen, und auf die Sitemap verweist

### Google Search Console (manueller Schritt, nicht Teil des Codes)
- Kurze Anleitung als README-Abschnitt: wie man die fertige Seite bei Google Search Console anmeldet und die Sitemap einreicht

## Workflow für neue Einträge unterwegs
1. Foto(s) machen, Text überlegen (ggf. mit Claude-Hilfe formulieren lassen)
2. Neue Markdown- oder HTML-Datei nach vorhandenem Muster erstellen (Dateiname mit Datum)
3. Datei + Fotos direkt über die **GitHub-App** oder die mobile Weboberfläche von GitHub ins Repository hochladen
4. Bei Verwendung von Netlify: automatischer Neu-Build und Veröffentlichung innerhalb weniger Minuten
5. Bei reinem GitHub Pages ohne Build-Skript: HTML-Datei ist sofort live, keine Wartezeit

## Konfigurierbare Konstanten (oben im Projekt, leicht anpassbar)
```
SITE_TITLE = "USA Roadtrip 2026"
SITE_DESCRIPTION = "Familien-Roadtrip von Las Vegas bis San Francisco"
BASE_URL = "https://<platzhalter>.github.io/<repo-name>/"  (oder eigene Domain später)
```

## Nicht im Scope (Version 1)
- Keine Kommentarfunktion
- Kein CMS/Admin-Oberfläche – Einträge werden als Dateien direkt im Repository verwaltet
- Keine automatische Bildkomprimierung (Fotos vorher ggf. manuell verkleinern, damit die Seite schnell lädt)
- Keine Mehrsprachigkeit

## Akzeptanzkriterien
- [ ] Seite lässt sich lokal im Browser öffnen und testen, ohne Server (bzw. mit einfachem lokalen Vorschau-Befehl, falls ein Build-Skript verwendet wird)
- [ ] Neuer Blogeintrag durch Hinzufügen einer einzelnen Datei möglich, ohne bestehenden Code zu ändern
- [ ] Alle Seiten haben individuelle Title- und Description-Meta-Tags
- [ ] `sitemap.xml` und `robots.txt` vorhanden und korrekt verlinkt
- [ ] Seite sieht auf einem Handy-Bildschirm (schmale Breite) gut aus, ohne horizontales Scrollen
- [ ] Fotos werden responsive dargestellt (keine Überbreite, kein Verzerren)
- [ ] README enthält kurze Anleitung: GitHub-Pages/Netlify-Einrichtung + Google Search Console-Anmeldung
