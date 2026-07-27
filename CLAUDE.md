# Hinweise für Claude

Statischer Reiseblog für einen Familien-Roadtrip durch den Südwesten der USA,
9.–28. August 2026, Las Vegas → San Francisco. Gebaut mit einem eigenen
Python-Skript, veröffentlicht auf GitHub Pages.

## Was hier wichtig ist

Der Blog wird **unterwegs vom Handy** befüllt, oft abends, oft bei schlechtem
Empfang. Deshalb gilt: ein neuer Eintrag ist immer nur eine neue Datei in einem
neuen Ordner. Niemals bestehenden Code ändern müssen, um einen Post zu
veröffentlichen. Wenn eine Änderung diesen Grundsatz verletzt, ist sie falsch.

## Anonymität

Der Blog bleibt anonym – das ist der Familie wichtig, nicht nur eine Stilfrage.

- Keine Fotos, auf denen wir (die Familie) erkennbar zu sehen sind. Landschaft,
  Fahrzeug, Essen, Hände, Rückenansichten: ja. Gesichter: nein.
- Nirgendwo der volle echte Name – weder im Fließtext noch in Konfiguration,
  Seitentitel oder Code-Kommentaren.
- Das GitHub-Handle ist bewusst schon anonym gewählt und bleibt es.

## Einen neuen Beitrag anlegen

Ordner nach dem Muster `posts/JJJJ-MM-TT-kurzer-titel/`, darin `index.md`:

```markdown
---
titel: South Rim, kurz nach sechs
ort: Grand Canyon
km: 450
teaser: Erster Blick über den Südrand – und deutlich kälter als gedacht.
---

Fließtext, ganz normale Absätze durch Leerzeilen getrennt.
```

Regeln dazu:

- Nur `titel` ist wirklich nötig. Fehlt er, wird er aus dem Ordnernamen abgeleitet.
- Das **Datum kommt aus dem Ordnernamen**. Eine `datum:`-Zeile überschreibt das.
- `km:` ist der Kilometerstand der Reise und erscheint als grünes Kästchen vor
  dem Datum. Fehlt die Zeile, entfällt das Kästchen ersatzlos.
- Fehlt `teaser`, nimmt der Build die ersten beiden Sätze des Textes.
- `cover: dateiname.jpg` wählt das Vorschaubild, sonst das alphabetisch erste Foto.
- `entwurf: true` hält den Beitrag aus dem Build heraus.
- Fotos kommen als `.jpg` einfach in denselben Ordner. Alles, was nicht im Text
  eingebunden ist, landet automatisch als Galerie unter dem Beitrag.
- Ein Beitrag ohne Fotos darf auch flach als `posts/JJJJ-MM-TT-titel.md` liegen.

## Ton

Erste Person Plural, knapp, konkret, keine Reiseführer-Prosa und keine
Superlative. Was tatsächlich passiert ist, gern mit einem beobachteten Detail.
Zwei bis fünf Absätze reichen. Keine Emojis.

## Unterstütztes Markdown

Der Parser in `build.py` kann bewusst nur eine Teilmenge: Überschriften (`##`),
Absätze, `**fett**`, `*kursiv*`, Links, Bilder, Aufzählungen, nummerierte
Listen, Zitate (`>`), Trennlinien (`---`), Code in Backticks. **Keine Tabellen,
kein eingebettetes HTML** – beides wird als Text ausgegeben.

## Aufbau

| Pfad | Zweck |
|---|---|
| `build.py` | Der komplette Generator. Nur Standardbibliothek, Pillow optional. |
| `site.config.json` | Titel, Beschreibung, `base_url`, Intro-Text, Bildbreiten |
| `templates/` | HTML-Gerüste mit `{{platzhalter}}` |
| `assets/style.css` | Alle Farben und Maße als Variablen im `:root`-Block oben |
| `posts/` | Ein Ordner pro Beitrag |
| `pages/` | Wird zu je einer Seite auf oberster Ebene plus Eintrag in der Fußzeile |
| `dist/` | Build-Ergebnis, nicht eingecheckt |

## Beim Arbeiten am Code beachten

- **Der Build darf nie hart abbrechen.** Fehlerhafte Eingaben bekommen einen
  Rückfall und eine Warnung über `warn()`, keine Exception. Ein kaputter Post
  darf nicht die ganze Seite blockieren.
- **Nur relative Pfade** in den generierten Seiten, damit `dist/index.html` auch
  per Doppelklick ohne Server funktioniert. Absolute URLs nur in `canonical`,
  `og:image` und `sitemap.xml`.
- **Pillow bleibt optional.** Ohne Pillow werden Fotos unverändert kopiert.
  Kein Codepfad darf einen Import davon voraussetzen.
- Beim Neukodieren werden EXIF-Daten entfernt. Das ist Absicht: Handyfotos
  enthalten GPS-Koordinaten, und die sollen nicht auf einer öffentlichen Seite
  landen. Diese Eigenschaft nicht wegoptimieren.

## Bauen

```
python build.py            # nach dist/
python build.py --serve    # zusätzlich http://localhost:8080
```
