# USA Roadtrip 2026

Statischer Reiseblog für unseren Familien-Roadtrip von Las Vegas nach San
Francisco, 9.–28. August 2026. Live unter
**https://thebluemic.github.io/reiseblog/**

Kein CMS, keine Datenbank, kein Login. Ein neuer Eintrag ist eine neue Datei in
einem neuen Ordner – mehr nicht. Alles andere (Startseite, Galerie, Sitemap,
Meta-Tags) entsteht beim Bauen von selbst.

---

## Einen neuen Eintrag schreiben

Ein Eintrag besteht aus einem Ordner mit dem Datum im Namen und einer Datei
`index.md` darin. Die Fotos liegen einfach daneben:

```
posts/
└── 2026-08-14-sequoia/
    ├── index.md
    ├── IMG_4821.jpg
    └── IMG_4822.jpg
```

Und so sieht `index.md` aus:

```markdown
---
titel: Zwischen den Riesen
ort: Sequoia National Park
teaser: Man kann Kindern hundertmal erzählen, wie groß ein Mammutbaum ist.
---

Um acht am Eingang, und trotzdem war der Parkplatz am General Sherman Tree
schon halb voll.

Der Weg runter ist kurz, der Weg hoch nicht.
```

**Pflicht ist nur `titel`.** Alles andere darf fehlen:

| Zeile | Wenn sie fehlt |
|---|---|
| `titel:` | wird aus dem Ordnernamen gebaut |
| `datum:` | kommt aus dem Ordnernamen (`2026-08-14-…`) |
| `teaser:` | die ersten beiden Sätze des Textes |
| `ort:` | steht dann einfach nicht dabei |
| `cover:` | das alphabetisch erste Foto im Ordner |
| `entwurf: true` | der Eintrag erscheint nicht auf der Seite |

Alle Fotos im Ordner landen automatisch als Galerie unter dem Text. Wer ein Foto
mitten im Text haben will, schreibt `![Was man sieht](IMG_4821.jpg)` – dieses
Bild taucht dann nicht noch einmal in der Galerie auf.

Ein Eintrag ganz ohne Fotos darf auch flach als `posts/2026-08-14-sequoia.md`
liegen.

### Was der Text kann

`## Zwischenüberschrift`, `**fett**`, `*kursiv*`, `[Link](https://…)`,
Aufzählungen mit `-`, nummerierte Listen, Zitate mit `>`, Trennlinien `---`,
`Code` in Backticks.

**Keine Tabellen, kein HTML.** Beides würde als roher Text auf der Seite landen.

---

## Unterwegs veröffentlichen

Drei Wege, je nachdem wie gut das Internet gerade ist.

### Mit stabilem Internet: Claude Code im Browser

[claude.ai/code](https://claude.ai/code) öffnen, dieses Repository auswählen,
Stichpunkte diktieren. Die Datei `CLAUDE.md` im Repo beschreibt Format und Ton,
Claude legt den Ordner an und committet. Zwei Minuten später ist es live.

### Mit wenig Internet: die Claude-App

[`docs/post-prompt.md`](docs/post-prompt.md) enthält einen fertigen Prompt zum
Kopieren. Claude fragt nach Stichpunkten und gibt Ordnernamen und fertige Datei
zurück. Danach bei GitHub im Browser:

1. **Add file → Create new file**
2. Als Dateinamen den ganzen Pfad eintippen:
   `posts/2026-08-14-sequoia/index.md` – die Schrägstriche legen den Ordner an
3. Text einfügen, **Commit changes**
4. In den neuen Ordner wechseln → **Add file → Upload files** → Fotos auswählen

### Ohne Internet

Den Text in einer beliebigen Notizen-App vorschreiben – das Format ist so
einfach, dass es von Hand funktioniert: drei Bindestriche, `titel:`, `ort:`,
`teaser:`, drei Bindestriche, dann der Text. Die Fotos des Tages in ein Album
sortieren. Abends im Hotel-WLAN beides in einem Rutsch hochladen.

---

## Fotos vor dem Upload verkleinern

**Lohnt sich, dauert eine halbe Minute pro Abend.** Ein Handyfoto ist 3–5 MB.
Acht Fotos sind 30 MB, die über Hotel-WLAN hochgeladen werden wollen – und die
danach für immer in der Versionsgeschichte des Repositories liegen. Verkleinert
sind es rund 300 KB pro Foto.

Unter Android geht das mit einem Batch-Resizer aus dem Play Store (z. B.
*Photo & Picture Resizer*): mehrere Bilder auswählen, längste Kante auf **1600
Pixel**, in einen eigenen Ordner speichern, den hochladen. **Einmal vor der
Reise ausprobieren**, damit unterwegs klar ist, wo die verkleinerten Bilder
landen.

Vergisst man es, ist nichts kaputt: der Build verkleinert beim Veröffentlichen
ohnehin noch einmal auf 800 und 1600 Pixel. Nur der Upload dauert dann länger.

### Was der Build mit den Fotos macht

- verkleinert auf 800 px und 1600 px und liefert per `srcset` die passende
  Größe aus – Handys laden die kleine
- **entfernt alle EXIF-Daten, inklusive der GPS-Koordinaten.** Handykameras
  schreiben die exakte Position ins Foto; auf einer öffentlichen Seite wäre
  sonst nachlesbar, wo wir jede Nacht waren
- rechnet die Drehung fest ein, damit Hochkantfotos nicht querliegen
- lässt bereits verarbeitete Fotos in Ruhe, der zweite Build ist schnell

---

## Lokal bauen und anschauen

Nötig ist Python 3 (ist auf dem Rechner installiert). Einmalig:

```
python -m pip install -r requirements.txt
```

Dann:

```
python build.py            # baut nach dist/
python build.py --serve    # baut und startet http://localhost:8080
```

Die fertige Seite liegt in `dist/`. `dist/index.html` lässt sich per Doppelklick
im Browser öffnen, ganz ohne Server – alle internen Links sind relativ.

Pillow ist **optional**: fehlt es, werden die Fotos unverändert kopiert und der
Build gibt einen Hinweis aus. Er bricht nie ab. Auch ein Eintrag mit kaputtem
Kopf oder fehlendem Titel blockiert die Seite nicht, sondern erzeugt eine
Warnung am Ende des Build-Logs.

---

## Aufbau

| Pfad | Zweck |
|---|---|
| `build.py` | der komplette Generator, eine Datei |
| `site.config.json` | Titel, Beschreibung, URL, Intro, Bildbreiten |
| `posts/` | ein Ordner pro Eintrag |
| `pages/` | wird zu je einer Seite oben auf der Ebene der Startseite |
| `templates/` | HTML-Gerüste mit `{{platzhalter}}` |
| `assets/style.css` | Farben und Maße als Variablen im `:root`-Block oben |
| `dist/` | Ergebnis des Builds, nicht eingecheckt |

Farben ändern: in `assets/style.css` stehen ganz oben alle Werte an einer
Stelle. Dort einen Wert anpassen reicht.

---

## Veröffentlichung

Jeder Push auf `main` startet die GitHub Action
[`.github/workflows/deploy.yml`](.github/workflows/deploy.yml): sie installiert
Pillow, baut die Seite und schiebt `dist/` zu GitHub Pages. Dauert etwa eine
Minute. Läuft etwas schief, bleibt die alte Version online und die Action ist im
Reiter **Actions** rot.

### Pages einrichten (einmalig, ist erledigt)

Repository → **Settings → Pages → Source: GitHub Actions**.

### Bei Google anmelden (einmalig, manueller Schritt)

1. [search.google.com/search-console](https://search.google.com/search-console)
   öffnen und mit dem Google-Konto anmelden
2. **Property hinzufügen → URL-Präfix**, dort
   `https://thebluemic.github.io/reiseblog/` eintragen
3. Bestätigung über die Methode **HTML-Tag**: Google zeigt eine Zeile
   `<meta name="google-site-verification" content="…">`. Diese Zeile in
   `templates/base.html` in den `<head>` einfügen, committen, warten bis die
   Action durch ist, dann in der Search Console auf **Bestätigen** klicken
4. Danach unter **Sitemaps** eintragen: `sitemap.xml`

Bis die ersten Einträge bei Google auftauchen, dauert es meist ein paar Tage.
