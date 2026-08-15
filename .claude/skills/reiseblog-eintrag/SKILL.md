---
name: reiseblog-eintrag
description: Führt durch das Anlegen eines neuen Eintrags im Reiseblog (posts/JJJJ-MM-TT-titel/) - fragt gezielt Ort, km-Stand, Stichpunkte und Fotos ab, schreibt den Post im richtigen Ton, prüft Anonymität und committet ihn. Immer verwenden, wenn der Nutzer einen neuen Blogpost, Reiseblog-Eintrag oder Beitrag anlegen, schreiben oder veröffentlichen will - auch bei knappen Formulierungen wie "neuer Post", "leg einen Eintrag an", "schreib was über heute" oder wenn er nur Stichpunkte zu einem Tag/Ort in den Chat wirft, ohne den Blog explizit zu erwähnen.
---

# Reiseblog-Eintrag anlegen

Dieser Skill führt durch das Anlegen eines neuen Posts für den Reiseblog. Der
Blog wird unterwegs vom Handy befüllt, oft abends, oft bei schlechtem Empfang
- der Ablauf hier ist bewusst kurz gehalten: nur das erfragen, was für den
Post wirklich fehlt, den Rest selbst erledigen.

Lies `CLAUDE.md` im Repo-Root, falls noch nicht im Kontext - dort stehen die
verbindlichen Grundregeln (Anonymität, Ton, Frontmatter-Felder). Dieser Skill
fasst sie handlungsorientiert zusammen, ersetzt sie aber nicht.

## 1. Eckdaten erfragen

Frag kompakt (nicht Feld für Feld einzeln, wenn es sich vermeiden lässt) nach:

- **Ort** - wo war das?
- **Datum** - Default: heute. Nur nachfragen, wenn aus dem Gespräch nicht
  klar ist, ob es um heute geht.
- **km-Stand** - optional. Nur übernehmen, wenn der Nutzer eine Zahl nennt;
  nicht raten oder schätzen. Ohne Angabe bleibt das Feld einfach weg.
- **Stichpunkte oder Text** zu dem, was passiert ist - das ist der
  eigentliche Inhalt, hier lohnt sich eine offene Nachfrage statt eines
  Formulars.
- **Fotos** - liegen welche vor, und wenn ja, wo (Pfad/Dateiname)? Optional
  ein gewünschtes Titelbild (`cover`).
- **Entwurf?** - nur fragen, wenn ein Grund dafür erkennbar ist (z. B. Text
  noch unvollständig). Default ist ein fertiger, veröffentlichter Post.

Wenn der Nutzer die Stichpunkte schon im ersten Prompt mitliefert, nicht
trotzdem nochmal alles einzeln nachfragen - nur das ergänzen, was wirklich
fehlt.

## 2. Text schreiben

Ton-Leitplanken aus `CLAUDE.md`, hier als schnelle Referenz:

- Erste Person Plural, knapp, konkret. Zwei bis fünf Absätze reichen.
- Keine Reiseführer-Prosa, keine Superlative, keine Emojis.
- Ein tatsächlich beobachtetes Detail ist mehr wert als eine allgemeine
  Beschreibung. Nicht "atemberaubender Ausblick", sondern was konkret
  passiert ist.
- Wohlgesinnt und positiv erzählen. Pannen, Wartezeiten oder Ärger dürfen
  als Fakt vorkommen, aber nicht den Ton dominieren oder den Aufhänger
  (Titel, Teaser, erster Satz) bilden - das Positive/Schöne am Tag verdient
  das Hauptgewicht. Also lieber knapp erwähnen und weiterziehen als
  drauf rumreiten, und wenn möglich mit einer positiven Wendung oder einem
  versöhnlichen Schlusssatz abschließen statt mit dem Ärger zu enden.

Zwei Auszüge aus echten Posts als Maßstab, wie knapp und konkret das gemeint
ist:

> Um halb fünf aus Tusayan losgefahren, damit wir vor der Hitze am Rand
> stehen. Der Parkplatz am Mather Point war schon halb voll, und trotzdem hat
> auf den letzten Metern niemand geredet.
>
> Die Kinder haben zuerst gar nichts gesagt. Erst nach ein paar Minuten kam
> die Frage, wo das denn aufhört. Gute Frage.

> Aufgesetzt haben wir das Ganze mit Claude Code. Das Skript, das aus einem
> Ordner mit `index.md` und ein paar Fotos eine fertige Seite macht, war in
> kurzer Zeit fertig.

Aus Stichpunkten des Nutzers einen Fließtext in diesem Ton machen - nicht
einfach die Stichpunkte aneinanderreihen.

## 3. Anonymitäts-Check (nicht überspringen)

Das ist der Familie explizit wichtig, nicht nur eine Stilfrage - deshalb hier
als eigener Schritt statt als Nebensatz:

- **Fotos**: jedes Foto, das in den Post-Ordner kommt, mit dem Read-Tool
  ansehen und auf erkennbare Gesichter prüfen. Landschaft, Fahrzeug, Essen,
  Hände, Rückenansichten sind unproblematisch.
- **Text**: keinen vollen echten Namen verwenden - weder im Fließtext noch
  im Frontmatter (z. B. `titel`, `teaser`).

Fotoauswahl ist Sache des Nutzers, nicht des Skills - der Nutzer wählt seine
Fotos bewusst aus und weiß selbst am besten, was er zeigen will. Bei einem
Foto mit erkennbarem Gesicht deshalb **nicht eigenmächtig weglassen,
zuschneiden oder unkenntlich machen**. Stattdessen kurz warnen ("Foto X
zeigt ein erkennbares Gesicht") und knapp nachfragen, ob es so rein soll,
raus soll oder anonymisiert werden soll - und erst danach entsprechend der
Antwort handeln. Bei mehreren Fotos die Warnungen bündeln, nicht für jedes
einzeln nachfragen.

Bevor der Post fertiggestellt wird, kurz explizit bestätigen (im Chat an den
Nutzer, nicht nur stillschweigend annehmen): "Fotos geprüft, keine
erkennbaren Gesichter" bzw. das Ergebnis der Rückfrage oben, falls doch
welche gefunden wurden. Fehlen Fotos ganz, das entsprechend vermerken.

## 4. Datei anlegen

Konvention aus `build.py`, exakt einhalten:

- Ordner `posts/JJJJ-MM-TT-titel/` (Datum kommt aus dem Ordnernamen, Titel
  im Ordnernamen ist ein kurzer Slug, nicht der volle Titeltext).
- Darin `index.md` mit Frontmatter-Block:

```markdown
---
titel: Kurzer, konkreter Titel
ort: Ortsname
km: 450
teaser: Ein bis zwei Sätze, falls nicht ohnehin aus dem Text ableitbar.
cover: dateiname.jpg
---

Fließtext in Absätzen.
```

- Nur `titel` ist wirklich nötig - fehlende Felder (`km`, `teaser`, `cover`,
  `entwurf`) einfach weglassen, nicht mit Platzhaltern auffüllen.
- Ein Post ganz ohne Fotos darf auch flach als `posts/JJJJ-MM-TT-titel.md`
  liegen, ohne eigenen Ordner.
- Fotos einfach unverändert in den Post-Ordner kopieren. Kein manuelles
  EXIF-Entfernen nötig - das übernimmt `build.py` beim Reencode automatisch
  (Absicht wegen GPS-Daten in Handyfotos, siehe `CLAUDE.md`).
- Fotos möglichst passend im Text platzieren (`![Alt-Text](dateiname.jpg)`
  direkt bei der Textstelle, zu der sie gehören), statt sie unsortiert am
  Ende in der automatischen Galerie landen zu lassen. Mehrere Fotos zur
  selben Textstelle dürfen als kleiner Block direkt hintereinander stehen.
  Nur Fotos ganz ohne erkennbaren Bezug zum Text bleiben unreferenziert
  und landen automatisch in der Galerie.

**Wichtig:** Für einen neuen Post ist nie eine Änderung an `build.py`,
`templates/` oder `assets/` nötig - das ist ein Grundprinzip dieses Repos,
gerade weil Posts oft unterwegs mit schlechter Verbindung angelegt werden.
Falls eine gewünschte Änderung das verletzen würde, kurz innehalten und dem
Nutzer sagen, warum, statt einfach am Code zu arbeiten.

## 5. Build-Check

Nach dem Schreiben einmal `python build.py` laufen lassen. Der Build bricht
laut Design nie hart ab, sondern gibt Warnungen über `warn()` aus - also
insbesondere auf Warnungen in der Ausgabe achten, nicht nur auf den Exit-Code,
und die dem Nutzer zeigen, falls welche auftauchen.

## 6. Vorschau zeigen und auf OK warten

Bevor irgendetwas gepusht wird, die fertige `index.md` als Artefakt anzeigen
(Markdown reicht, kein aufwendiges Design nötig) und auf die ausdrückliche
Bestätigung des Nutzers warten. Das ist die einzige Rückfrage in diesem
Ablauf - aber sie ist Pflicht, auch wenn alles andere (Fotos, Build)
unauffällig war. Erst nach einem klaren OK weiter zu Schritt 7.

## 7. Commit, Push und Merge - in einem Rutsch

Neue Post-Dateien (und ggf. Fotos) automatisch committen, z. B.:

```
git add posts/JJJJ-MM-TT-titel/
git commit -m "Neuer Eintrag: <titel>"
```

Der Nutzer will außer der Vorschau-Bestätigung aus Schritt 6 **keine
weiteren Rückfragen** - das widerspräche dem "unterwegs vom Handy"-Grundsatz,
wenn jeder einzelne Schritt noch eine eigene Nachfrage bräuchte. Nach dem OK
deshalb in einem Zug erledigen, ohne Zwischenstopp:

1. `git push` auf den aktuellen Arbeits-Branch
2. Pull Request nach `main` erstellen (falls noch keiner offen ist)
3. Den PR direkt mergen

Nur wenn der Build-Check in Schritt 5 Warnungen zeigt oder etwas sonst
auffällig ist, das schon in der Vorschau aus Schritt 6 mit ansprechen -
nicht erst nach dem OK überraschend nachliefern.

## Modell-Hinweis

Für diesen Skill eignet sich Sonnet besser als ein kleineres/schnelleres
Modell wie Haiku: Die eigentliche Schwierigkeit liegt im Ton (knapp, ohne
Kitsch, mit einem beobachteten Detail statt allgemeiner Beschreibung), nicht
in mechanischer Arbeit. Das ist eine Stilaufgabe, bei der ein stärkeres
Modell zuverlässiger trifft - und da Posts selten und kurz sind, fällt der
Kostenunterschied kaum ins Gewicht.
