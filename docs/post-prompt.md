# Vorlage für die Claude-App

Für unterwegs, wenn das Internet nur für ein Chatfenster reicht. Den Text unten
komplett kopieren, in die Claude-App einfügen, abschicken. Claude fragt dann
nach Stichpunkten und liefert eine fertige Datei zurück, die nur noch bei GitHub
eingefügt werden muss.

---

Du hilfst mir, einen Eintrag für unseren Reiseblog zu schreiben. Wir sind eine
Familie aus Deutschland und machen im August 2026 einen Roadtrip von Las Vegas
nach San Francisco.

Frag mich zuerst nach: Datum, Ort und was an dem Tag passiert ist. Stell ruhig
ein, zwei Rückfragen, wenn meine Stichpunkte zu dünn sind.

Schreib danach den Eintrag in diesem Ton:

- erste Person Plural, knapp und konkret
- keine Reiseführer-Prosa, keine Superlative, keine Emojis
- zwei bis fünf Absätze
- mindestens ein beobachtetes Detail, das nur wir gesehen haben können

Gib mir am Ende genau zwei Dinge aus:

**1. Den Ordnernamen** nach dem Muster `posts/JJJJ-MM-TT-kurzer-titel/`
– Kleinbuchstaben, Bindestriche statt Leerzeichen, keine Umlaute
(ä→ae, ö→oe, ü→ue, ß→ss).

**2. Den kompletten Inhalt der Datei `index.md`** in einem Codeblock, damit ich
ihn in einem Stück kopieren kann:

```markdown
---
titel: <Titel des Eintrags>
ort: <Ort>
teaser: <ein Satz, der Lust aufs Weiterlesen macht, maximal 200 Zeichen>
---

<Der Fließtext.>
```

Wichtig zum Format: Im Text darf nur einfaches Markdown vorkommen –
Überschriften mit `##`, `**fett**`, `*kursiv*`, Links, Aufzählungen mit `-`,
Zitate mit `>`. **Keine Tabellen und kein HTML**, die kann unser Generator
nicht. Bilder brauchst du nicht einzubauen: die Fotos lade ich in denselben
Ordner hoch, sie erscheinen automatisch als Galerie unter dem Text.
