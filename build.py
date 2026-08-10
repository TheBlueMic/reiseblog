#!/usr/bin/env python3
"""
Baut den statischen Reiseblog aus posts/ und pages/ nach dist/.

    python build.py            einmal bauen
    python build.py --serve    bauen und unter http://localhost:8080 ausliefern

Der Build bricht absichtlich nie hart ab: fehlt ein Titel, ist das Frontmatter
kaputt oder zeigt ein Bildlink ins Leere, wird ein sinnvoller Rückfall benutzt
und eine Warnung gesammelt. Ein hastig geschriebener Eintrag soll online gehen,
nicht die ganze Seite blockieren.

Pillow ist optional. Fehlt es, werden die Fotos unverändert kopiert.
"""

import html
import json
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

try:
    from PIL import Image, ImageOps
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

ROOT = Path(__file__).parent.resolve()
DIST = ROOT / "dist"
POSTS_DIR = ROOT / "posts"
PAGES_DIR = ROOT / "pages"
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni",
          "Juli", "August", "September", "Oktober", "November", "Dezember"]

warnings: list[str] = []


def warn(message: str) -> None:
    warnings.append(message)


# ---------------------------------------------------------------- Konfiguration

def load_config() -> dict:
    defaults = {
        "site_title": "Reiseblog",
        "site_description": "",
        "base_url": "",
        "kicker": "",
        "intro": "",
        "language": "de",
        "image_widths": [800, 1600],
        "image_quality": 82,
    }
    path = ROOT / "site.config.json"
    if not path.exists():
        warn("site.config.json fehlt – es werden Standardwerte benutzt.")
        return defaults
    try:
        defaults.update(json.loads(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError as exc:
        warn(f"site.config.json ist kein gültiges JSON ({exc}) – Standardwerte werden benutzt.")
    if not defaults["base_url"]:
        warn("base_url ist leer – canonical, og:image und sitemap.xml bleiben unvollständig.")
    elif not defaults["base_url"].endswith("/"):
        defaults["base_url"] += "/"
    return defaults


# ---------------------------------------------------------------- Frontmatter

def parse_frontmatter(text: str, quelle: str) -> tuple[dict, str]:
    """Liest einen einfachen ``key: wert``-Kopf zwischen zwei ----Zeilen."""
    if not text.lstrip().startswith("---"):
        return {}, text

    text = text.lstrip()
    parts = text.split("\n", 1)
    rest = parts[1] if len(parts) > 1 else ""
    ende = rest.find("\n---")
    if ende == -1:
        warn(f"{quelle}: Der Kopf wird nicht durch eine zweite ----Zeile geschlossen. "
             f"Der ganze Text wird als Inhalt behandelt.")
        return {}, text

    kopf = rest[:ende]
    koerper = rest[ende + 4:].lstrip("\n")

    daten = {}
    for zeile in kopf.splitlines():
        zeile = zeile.strip()
        if not zeile or zeile.startswith("#"):
            continue
        if ":" not in zeile:
            warn(f"{quelle}: Kopfzeile ohne Doppelpunkt wird übersprungen: {zeile!r}")
            continue
        schluessel, wert = zeile.split(":", 1)
        daten[schluessel.strip().lower()] = wert.strip().strip('"').strip("'")
    return daten, koerper


def feld(daten: dict, *namen: str, default: str = "") -> str:
    for name in namen:
        if daten.get(name):
            return daten[name]
    return default


def ist_wahr(wert: str) -> bool:
    return str(wert).strip().lower() in {"true", "ja", "yes", "1"}


# ---------------------------------------------------------------- Markdown

CODE_RE = re.compile(r"`([^`]+)`")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(\s*([^)\s]+)\s*\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(\s*([^)\s]+)\s*\)")
BOLD_RE = re.compile(r"\*\*(\S(?:[^*]*\S)?)\*\*")
ITALIC_STAR_RE = re.compile(r"(?<![\*\w])\*(\S(?:[^*\n]*\S)?)\*(?!\*)")
ITALIC_UNDER_RE = re.compile(r"(?<![_\w])_(\S(?:[^_\n]*\S)?)_(?![_\w])")


def inline(text: str, bild_html) -> str:
    """Wandelt Auszeichnungen innerhalb einer Zeile um. HTML wird vorher entschärft."""
    text = html.escape(text, quote=False)

    # Code-Spannen herausnehmen, damit darin nichts weiter ersetzt wird.
    depots: list[str] = []

    def depot(treffer):
        depots.append(f"<code>{treffer.group(1)}</code>")
        return f"\x00{len(depots) - 1}\x00"

    text = CODE_RE.sub(depot, text)

    def bild(treffer):
        depots.append(bild_html(treffer.group(2), treffer.group(1)))
        return f"\x00{len(depots) - 1}\x00"

    text = IMG_RE.sub(bild, text)

    def link(treffer):
        # Die Zeile wurde oben schon mit html.escape() behandelt (& und < > sind
        # also schon Entities) – hier nur noch Anführungszeichen für das Attribut.
        ziel = treffer.group(2).replace('"', "&quot;")
        extern = ' target="_blank" rel="noopener"' if ziel.startswith("http") else ""
        return f'<a href="{ziel}"{extern}>{treffer.group(1)}</a>'

    text = LINK_RE.sub(link, text)
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = ITALIC_STAR_RE.sub(r"<em>\1</em>", text)
    text = ITALIC_UNDER_RE.sub(r"<em>\1</em>", text)

    for nummer, inhalt in enumerate(depots):
        text = text.replace(f"\x00{nummer}\x00", inhalt)
    return text


def markdown(text: str, bild_html) -> str:
    """Unterstützte Teilmenge: Überschriften, Absätze, fett, kursiv, Links,
    Bilder, Aufzählungen, nummerierte Listen, Zitate, Trennlinien."""
    zeilen = text.replace("\r\n", "\n").split("\n")
    ausgabe: list[str] = []
    absatz: list[str] = []
    liste: list[str] = []
    listentyp = ""
    zitat: list[str] = []

    def absatz_schliessen():
        nonlocal absatz
        if absatz:
            inhalt = inline(" ".join(absatz), bild_html)
            # Ein alleinstehendes Bild braucht kein <p> drumherum.
            if inhalt.startswith("<figure") and inhalt.endswith("</figure>"):
                ausgabe.append(inhalt)
            else:
                ausgabe.append(f"<p>{inhalt}</p>")
            absatz = []

    def liste_schliessen():
        nonlocal liste, listentyp
        if liste:
            punkte = "".join(f"<li>{inline(p, bild_html)}</li>" for p in liste)
            ausgabe.append(f"<{listentyp}>{punkte}</{listentyp}>")
            liste, listentyp = [], ""

    def zitat_schliessen():
        nonlocal zitat
        if zitat:
            ausgabe.append(f"<blockquote><p>{inline(' '.join(zitat), bild_html)}</p></blockquote>")
            zitat = []

    def alles_schliessen():
        absatz_schliessen()
        liste_schliessen()
        zitat_schliessen()

    for zeile in zeilen:
        blank = not zeile.strip()
        if blank:
            alles_schliessen()
            continue

        if re.fullmatch(r"\s*(-{3,}|\*{3,}|_{3,})\s*", zeile):
            alles_schliessen()
            ausgabe.append("<hr>")
            continue

        ueberschrift = re.match(r"\s*(#{1,6})\s+(.*)", zeile)
        if ueberschrift:
            alles_schliessen()
            stufe = min(len(ueberschrift.group(1)) + 1, 6)  # h1 bleibt dem Seitentitel
            ausgabe.append(f"<h{stufe}>{inline(ueberschrift.group(2).strip(), bild_html)}</h{stufe}>")
            continue

        punkt = re.match(r"\s*[-*+]\s+(.*)", zeile)
        if punkt:
            absatz_schliessen()
            zitat_schliessen()
            if listentyp and listentyp != "ul":
                liste_schliessen()
            listentyp = "ul"
            liste.append(punkt.group(1).strip())
            continue

        nummer = re.match(r"\s*\d+[.)]\s+(.*)", zeile)
        if nummer:
            absatz_schliessen()
            zitat_schliessen()
            if listentyp and listentyp != "ol":
                liste_schliessen()
            listentyp = "ol"
            liste.append(nummer.group(1).strip())
            continue

        zitatzeile = re.match(r"\s*>\s?(.*)", zeile)
        if zitatzeile:
            absatz_schliessen()
            liste_schliessen()
            zitat.append(zitatzeile.group(1).strip())
            continue

        liste_schliessen()
        zitat_schliessen()
        absatz.append(zeile.strip())

    alles_schliessen()
    return "\n".join(ausgabe)


def nur_text(markdown_text: str) -> str:
    """Grobe Textfassung für Teaser und Meta-Beschreibungen."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", markdown_text)
    text = LINK_RE.sub(r"\1", text)
    text = re.sub(r"[*_`#>]", "", text)
    return " ".join(text.split())


def teaser_aus(text: str, grenze: int = 200) -> str:
    klartext = nur_text(text)
    if not klartext:
        return ""
    saetze = re.split(r"(?<=[.!?])\s+", klartext)
    ergebnis = " ".join(saetze[:2]).strip()
    if len(ergebnis) > grenze:
        ergebnis = ergebnis[:grenze].rsplit(" ", 1)[0] + " …"
    return ergebnis


# ---------------------------------------------------------------- Bilder

statistik = {"bilder": 0, "bytes_vorher": 0, "bytes_nachher": 0, "uebersprungen": 0}


def bild_verarbeiten(quelle: Path, zielordner: Path, breiten: list[int], qualitaet: int) -> dict:
    """Erzeugt verkleinerte Fassungen ohne EXIF und gibt die Varianten zurück.

    Ohne Pillow wird die Datei unverändert kopiert. Der Rückgabewert hat immer
    dieselbe Form, damit der Rest des Skripts sich nicht dafür interessieren muss.
    """
    zielordner.mkdir(parents=True, exist_ok=True)
    original_groesse = quelle.stat().st_size
    statistik["bilder"] += 1
    statistik["bytes_vorher"] += original_groesse

    if not HAS_PILLOW:
        ziel = zielordner / quelle.name
        if not ziel.exists() or ziel.stat().st_mtime < quelle.stat().st_mtime:
            shutil.copy2(quelle, ziel)
        statistik["bytes_nachher"] += original_groesse
        return {"src": quelle.name, "srcset": "", "breite": 0, "hoehe": 0,
                "dateien": [quelle.name]}

    try:
        with Image.open(quelle) as bild:
            bild = ImageOps.exif_transpose(bild)          # Drehung fest einrechnen
            if bild.mode in ("P", "RGBA", "LA") and quelle.suffix.lower() in {".jpg", ".jpeg"}:
                bild = bild.convert("RGB")
            quell_breite, quell_hoehe = bild.size

            varianten = []
            for breite in sorted(breiten):
                if breite > quell_breite:
                    continue
                varianten.append(breite)
            if not varianten:
                varianten = [quell_breite]

            erzeugt = []
            for breite in varianten:
                name = f"{quelle.stem}-{breite}{quelle.suffix.lower()}"
                ziel = zielordner / name
                if ziel.exists() and ziel.stat().st_mtime >= quelle.stat().st_mtime:
                    statistik["uebersprungen"] += 1
                else:
                    hoehe = round(quell_hoehe * breite / quell_breite)
                    kopie = bild.resize((breite, hoehe), Image.LANCZOS)
                    if quelle.suffix.lower() in {".jpg", ".jpeg"}:
                        kopie = kopie.convert("RGB")
                        kopie.save(ziel, "JPEG", quality=qualitaet, optimize=True,
                                   progressive=True)
                    else:
                        kopie.save(ziel, optimize=True)   # ohne exif= wird kein EXIF geschrieben
                erzeugt.append((breite, name, ziel))

            statistik["bytes_nachher"] += sum(z.stat().st_size for _, _, z in erzeugt)
            groesste_breite, groesster_name, _ = erzeugt[-1]
            srcset = ", ".join(f"{name} {breite}w" for breite, name, _ in erzeugt)
            return {
                "src": groesster_name,
                "srcset": srcset if len(erzeugt) > 1 else "",
                "breite": groesste_breite,
                "hoehe": round(quell_hoehe * groesste_breite / quell_breite),
                "dateien": [name for _, name, _ in erzeugt],
            }
    except Exception as exc:                              # defektes oder exotisches Bild
        warn(f"{quelle.name}: konnte nicht verarbeitet werden ({exc}) – Original wird kopiert.")
        ziel = zielordner / quelle.name
        shutil.copy2(quelle, ziel)
        statistik["bytes_nachher"] += original_groesse
        return {"src": quelle.name, "srcset": "", "breite": 0, "hoehe": 0,
                "dateien": [quelle.name]}


def mit_prefix(variante: dict, prefix: str) -> dict:
    """Stellt den Bildvarianten einen Pfad voran – die Startseite liegt eine
    Ebene über den Fotos und braucht posts/<slug>/ davor."""
    if not prefix:
        return variante
    neu = dict(variante)
    neu["src"] = prefix + variante["src"]
    if variante["srcset"]:
        neu["srcset"] = ", ".join(prefix + teil.strip()
                                  for teil in variante["srcset"].split(","))
    return neu


def img_tag(variante: dict, alt: str, sizes: str, css_klasse: str = "") -> str:
    teile = [f'src="{html.escape(variante["src"], quote=True)}"']
    if variante["srcset"]:
        teile.append(f'srcset="{html.escape(variante["srcset"], quote=True)}"')
        teile.append(f'sizes="{sizes}"')
    if variante["breite"]:
        teile.append(f'width="{variante["breite"]}" height="{variante["hoehe"]}"')
    if css_klasse:
        teile.append(f'class="{css_klasse}"')
    teile.append(f'alt="{html.escape(alt, quote=True)}"')
    teile.append('loading="lazy" decoding="async"')
    return f"<img {' '.join(teile)}>"


# ---------------------------------------------------------------- Beiträge

DATUM_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-?(.*)$")


def datum_aus_slug(slug: str) -> tuple[date | None, str]:
    treffer = DATUM_RE.match(slug)
    if not treffer:
        return None, slug
    jahr, monat, tag, rest = treffer.groups()
    try:
        return date(int(jahr), int(monat), int(tag)), rest or slug
    except ValueError:
        return None, rest or slug


def datum_deutsch(wert: date) -> str:
    return f"{wert.day}. {MONATE[wert.month - 1]} {wert.year}"


def titel_aus_slug(rest: str) -> str:
    return rest.replace("-", " ").replace("_", " ").strip().capitalize() or "Ohne Titel"


def beitraege_einlesen() -> list[dict]:
    if not POSTS_DIR.exists():
        warn("Der Ordner posts/ fehlt – es gibt keine Einträge.")
        return []

    quellen: list[tuple[str, Path, Path | None]] = []
    for eintrag in sorted(POSTS_DIR.iterdir()):
        if eintrag.is_dir():
            markdown_datei = eintrag / "index.md"
            if not markdown_datei.exists():
                treffer = sorted(eintrag.glob("*.md"))
                if not treffer:
                    warn(f"posts/{eintrag.name}/ enthält keine .md-Datei und wird übersprungen.")
                    continue
                markdown_datei = treffer[0]
            quellen.append((eintrag.name, markdown_datei, eintrag))
        elif eintrag.suffix.lower() == ".md":
            quellen.append((eintrag.stem, eintrag, None))

    beitraege = []
    for slug, markdown_datei, bildordner in quellen:
        rohtext = markdown_datei.read_text(encoding="utf-8")
        kopf, koerper = parse_frontmatter(rohtext, f"posts/{slug}")

        if ist_wahr(feld(kopf, "entwurf", "draft")):
            continue

        wann, rest = datum_aus_slug(slug)
        datum_feld = feld(kopf, "datum", "date")
        if datum_feld:
            try:
                wann = datetime.strptime(datum_feld[:10], "%Y-%m-%d").date()
            except ValueError:
                warn(f"posts/{slug}: datum {datum_feld!r} ist nicht im Format JJJJ-MM-TT.")
        if wann is None:
            wann = date.fromtimestamp(markdown_datei.stat().st_mtime)
            warn(f"posts/{slug}: kein Datum im Ordnernamen und keine datum-Zeile – "
                 f"das Änderungsdatum der Datei wird benutzt ({wann}).")

        titel = feld(kopf, "titel", "title")
        if not titel:
            titel = titel_aus_slug(rest)
            warn(f"posts/{slug}: keine titel-Zeile – aus dem Ordnernamen abgeleitet: {titel!r}")

        bilder = []
        if bildordner:
            bilder = sorted(p for p in bildordner.iterdir()
                            if p.suffix.lower() in IMAGE_SUFFIXES)

        beitraege.append({
            "slug": slug,
            "titel": titel,
            "datum": wann,
            "ort": feld(kopf, "ort", "location"),
            "km": feld(kopf, "km", "kilometer"),
            "teaser": feld(kopf, "teaser", "beschreibung", "description"),
            "cover": feld(kopf, "cover", "titelbild"),
            "koerper": koerper,
            "bilder": bilder,
            "ordner": bildordner,
            "quelle": markdown_datei,
        })

    beitraege.sort(key=lambda b: (b["datum"], b["slug"]), reverse=True)
    return beitraege


# ---------------------------------------------------------------- Rendern

def template(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def fuellen(vorlage: str, werte: dict) -> str:
    for schluessel, wert in werte.items():
        vorlage = vorlage.replace("{{" + schluessel + "}}", str(wert))
    return vorlage


def seite_schreiben(ziel: Path, inhalt: str, *, cfg: dict, titel: str, beschreibung: str,
                    canonical: str, root: str, nav: str, og_typ: str = "website",
                    og_bild: str = "") -> None:
    og_tag = f'<meta property="og:image" content="{html.escape(og_bild, quote=True)}">\n' if og_bild else ""
    seite = fuellen(template("base.html"), {
        "language": cfg["language"],
        "title": html.escape(titel, quote=True),
        "description": html.escape(beschreibung, quote=True),
        "canonical": html.escape(canonical, quote=True),
        "og_type": og_typ,
        "og_title": html.escape(titel, quote=True),
        "og_image": og_tag,
        "site_title": html.escape(cfg["site_title"], quote=True),
        "root": root,
        "nav": nav,
        "content": inhalt,
    })
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(seite, encoding="utf-8")


def bauen() -> dict:
    cfg = load_config()
    basis = cfg["base_url"]

    if DIST.exists():
        # dist/ nicht komplett löschen: die verkleinerten Bilder sollen erhalten
        # bleiben, damit der nächste Build sie überspringen kann.
        for pfad in DIST.rglob("*.html"):
            pfad.unlink()
    DIST.mkdir(exist_ok=True)

    if ASSETS.exists():
        shutil.copytree(ASSETS, DIST / "assets", dirs_exist_ok=True)

    beitraege = beitraege_einlesen()
    seiten = sorted(PAGES_DIR.glob("*.md")) if PAGES_DIR.exists() else []

    # Navigation für die Fußzeile
    nav_eintraege = ['<a href="{root}index.html">Startseite</a>']
    seiten_titel = {}
    for seitendatei in seiten:
        kopf, _ = parse_frontmatter(seitendatei.read_text(encoding="utf-8"), f"pages/{seitendatei.name}")
        titel = feld(kopf, "titel", "title", default=titel_aus_slug(seitendatei.stem))
        seiten_titel[seitendatei.stem] = titel
        nav_eintraege.append(f'<a href="{{root}}{seitendatei.stem}.html">{html.escape(titel)}</a>')
    nav_vorlage = " · ".join(nav_eintraege)

    # ---- Beiträge
    item_vorlage = template("item.html")
    post_vorlage = template("post.html")
    eintraege_html = []

    for beitrag in beitraege:
        slug = beitrag["slug"]
        ziel_ordner = DIST / "posts" / slug
        root = "../../"
        nav = nav_vorlage.replace("{root}", root)

        varianten: dict[str, dict] = {}
        for bild in beitrag["bilder"]:
            varianten[bild.name] = bild_verarbeiten(
                bild, ziel_ordner, cfg["image_widths"], cfg["image_quality"])

        # Fotos aufräumen, die es in der Quelle nicht mehr gibt – sonst bleiben
        # umbenannte oder gelöschte Bilder lokal für immer in dist/ liegen.
        if ziel_ordner.exists():
            gewollt = {"index.html"}
            for variante in varianten.values():
                gewollt.update(variante.get("dateien", []))
            for datei in ziel_ordner.iterdir():
                if datei.is_file() and datei.name not in gewollt:
                    datei.unlink()

        im_text: set[str] = set()

        def bild_im_text(pfad: str, alt: str, _varianten=varianten, _im_text=im_text,
                         _slug=slug, _titel=beitrag["titel"]) -> str:
            name = pfad.split("/")[-1]
            if name not in _varianten:
                warn(f"posts/{_slug}: das Bild {pfad!r} steht im Text, liegt aber nicht im Ordner.")
                return f'<span class="fehlendes-bild">[Bild fehlt: {html.escape(name)}]</span>'
            _im_text.add(name)
            if not alt:
                warn(f"posts/{_slug}: {name} hat keinen Alternativtext (![Beschreibung](…)).")
            beschriftung = f'<figcaption>{html.escape(alt)}</figcaption>' if alt else ""
            tag = img_tag(_varianten[name], alt or _titel, "(max-width: 46rem) 100vw, 46rem")
            return f'<figure class="bild">{tag}{beschriftung}</figure>'

        koerper_html = markdown(beitrag["koerper"], bild_im_text)

        # Vorschaubild: cover aus dem Kopf, sonst das erste Foto im Ordner.
        # Es eröffnet den Beitrag und erscheint deshalb nicht noch einmal in
        # der Galerie – außer es steht ohnehin schon mitten im Text.
        cover_name = beitrag["cover"] or (beitrag["bilder"][0].name if beitrag["bilder"] else "")
        if beitrag["cover"] and beitrag["cover"] not in varianten:
            warn(f"posts/{slug}: cover {beitrag['cover']!r} liegt nicht im Ordner.")
            cover_name = beitrag["bilder"][0].name if beitrag["bilder"] else ""

        hero_html = ""
        if cover_name and cover_name not in im_text:
            hero_html = ('<div class="post-hero">'
                         + img_tag(varianten[cover_name], beitrag["titel"],
                                   "(max-width: 46rem) 100vw, 46rem")
                         + "</div>")

        bereits_gezeigt = im_text | ({cover_name} if hero_html else set())
        galerie_bilder = [b for b in beitrag["bilder"] if b.name not in bereits_gezeigt]
        if galerie_bilder:
            kacheln = []
            for nummer, bild in enumerate(galerie_bilder, start=1):
                alt = f"{beitrag['titel']} – Foto {nummer}"
                bild_tag = img_tag(varianten[bild.name], alt, "(max-width: 46rem) 50vw, 23rem")
                voll_src = html.escape(varianten[bild.name]["src"], quote=True)
                kacheln.append(f'<figure class="galerie-bild">'
                               f'<a href="{voll_src}" class="galerie-link">{bild_tag}</a>'
                               f'</figure>')
            galerie_html = f'<div class="galerie">{"".join(kacheln)}</div>'
        else:
            galerie_html = ""

        teaser = beitrag["teaser"] or teaser_aus(beitrag["koerper"])
        if not teaser:
            warn(f"posts/{slug}: kein Teaser und kein Text – die Beschreibung bleibt leer.")

        # Datumszeile: das grüne km-Kästchen nur, wenn km: im Kopf steht.
        meta_teile = []
        if beitrag["km"]:
            meta_teile.append(f'<span class="km">km {html.escape(beitrag["km"])}</span>')
        meta_teile.append(f'<span>{html.escape(datum_deutsch(beitrag["datum"]))}</span>')
        if beitrag["ort"]:
            meta_teile.append(f'<span>{html.escape(beitrag["ort"])}</span>')
        meta = "".join(meta_teile)

        inhalt = fuellen(post_vorlage, {
            "root": root,
            "hero": hero_html,
            "meta": meta,
            "title": html.escape(beitrag["titel"]),
            "body": koerper_html,
            "gallery": galerie_html,
        })

        canonical = f"{basis}posts/{slug}/" if basis else ""
        og_bild = f"{basis}posts/{slug}/{varianten[cover_name]['src']}" if (basis and cover_name) else ""

        seite_schreiben(ziel_ordner / "index.html", inhalt, cfg=cfg,
                        titel=f"{beitrag['titel']} – {cfg['site_title']}",
                        beschreibung=teaser, canonical=canonical, root=root, nav=nav,
                        og_typ="article", og_bild=og_bild)

        thumb = ""
        if cover_name:
            # Die Startseite liegt in dist/, die Fotos in dist/posts/<slug>/.
            vorschau = mit_prefix(varianten[cover_name], f"posts/{slug}/")
            thumb = ('<div class="feed-thumb">'
                     + img_tag(vorschau, f"Vorschaubild: {beitrag['titel']}",
                               "(max-width: 46rem) 100vw, 46rem")
                     + "</div>")

        eintraege_html.append(fuellen(item_vorlage, {
            "url": f"posts/{slug}/index.html",
            "thumb": thumb,
            "meta": meta,
            "title": html.escape(beitrag["titel"]),
            "teaser": html.escape(teaser),
        }))

    # ---- Startseite
    if not eintraege_html:
        eintraege_html.append('<p class="leer">Noch keine Einträge. Der erste kommt bald.</p>')

    startseite = fuellen(template("index.html"), {
        "kicker": html.escape(cfg["kicker"]),
        "site_title": html.escape(cfg["site_title"]),
        "intro": html.escape(cfg["intro"]),
        "items": "\n".join(eintraege_html),
    })
    seite_schreiben(DIST / "index.html", startseite, cfg=cfg,
                    titel=cfg["site_title"], beschreibung=cfg["site_description"],
                    canonical=basis, root="", nav=nav_vorlage.replace("{root}", ""))

    # ---- Weitere Seiten
    page_vorlage = template("page.html")
    for seitendatei in seiten:
        kopf, koerper = parse_frontmatter(seitendatei.read_text(encoding="utf-8"),
                                          f"pages/{seitendatei.name}")
        titel = seiten_titel[seitendatei.stem]
        beschreibung = feld(kopf, "beschreibung", "description") or teaser_aus(koerper)

        def kein_bild(pfad: str, alt: str, _name=seitendatei.name) -> str:
            warn(f"pages/{_name}: Bilder werden auf einfachen Seiten nicht verarbeitet ({pfad}).")
            return ""

        inhalt = fuellen(page_vorlage, {
            "root": "",
            "title": html.escape(titel),
            "body": markdown(koerper, kein_bild),
        })
        seite_schreiben(DIST / f"{seitendatei.stem}.html", inhalt, cfg=cfg,
                        titel=f"{titel} – {cfg['site_title']}", beschreibung=beschreibung,
                        canonical=f"{basis}{seitendatei.stem}.html" if basis else "",
                        root="", nav=nav_vorlage.replace("{root}", ""))

    # ---- 404
    seite_schreiben(DIST / "404.html",
                    '<main id="inhalt" class="post"><header class="post-head">'
                    '<h1 class="post-title">Diese Seite gibt es nicht</h1></header>'
                    '<div class="post-body"><p>Der Link führt ins Leere. '
                    '<a href="/index.html">Zurück zur Startseite</a>.</p></div></main>',
                    cfg=cfg, titel=f"Nicht gefunden – {cfg['site_title']}",
                    beschreibung="Diese Seite gibt es nicht.", canonical="", root="",
                    nav=nav_vorlage.replace("{root}", ""))

    # ---- sitemap.xml und robots.txt
    if basis:
        eintraege = [(basis, DIST / "index.html")]
        eintraege += [(f"{basis}posts/{b['slug']}/", DIST / "posts" / b["slug"] / "index.html")
                      for b in beitraege]
        eintraege += [(f"{basis}{s.stem}.html", DIST / f"{s.stem}.html") for s in seiten]

        zeilen = ['<?xml version="1.0" encoding="UTF-8"?>',
                  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for url, pfad in eintraege:
            stand = date.fromtimestamp(pfad.stat().st_mtime).isoformat() if pfad.exists() else ""
            zeilen.append(f"  <url><loc>{html.escape(url)}</loc>"
                          f"<lastmod>{stand}</lastmod></url>")
        zeilen.append("</urlset>")
        (DIST / "sitemap.xml").write_text("\n".join(zeilen) + "\n", encoding="utf-8")

        (DIST / "robots.txt").write_text(
            f"User-agent: *\nAllow: /\n\nSitemap: {basis}sitemap.xml\n", encoding="utf-8")
    else:
        warn("Ohne base_url werden sitemap.xml und robots.txt nicht geschrieben.")

    return {"beitraege": len(beitraege), "seiten": len(seiten)}


# ---------------------------------------------------------------- Ausgabe

def bericht(ergebnis: dict) -> None:
    print(f"\n  {ergebnis['beitraege']} Beiträge, {ergebnis['seiten']} weitere Seiten, "
          f"{statistik['bilder']} Fotos")

    if not HAS_PILLOW:
        print("  Pillow ist nicht installiert – Fotos wurden unverändert kopiert.")
        print("  Installieren mit:  python -m pip install Pillow")
    elif statistik["bytes_vorher"]:
        vorher = statistik["bytes_vorher"] / 1_048_576
        nachher = statistik["bytes_nachher"] / 1_048_576
        gespart = vorher - nachher
        vorzeichen = "–" if gespart >= 0 else "+"
        print(f"  Fotos: {vorher:.1f} MB → {nachher:.1f} MB "
              f"({vorzeichen}{abs(gespart):.1f} MB, EXIF inkl. GPS entfernt)")
        if statistik["uebersprungen"]:
            print(f"  {statistik['uebersprungen']} bereits verarbeitete Fassungen übersprungen")

    if warnings:
        print(f"\n  {len(warnings)} Hinweis(e):")
        for eintrag in warnings:
            print(f"    · {eintrag}")
    print(f"\n  Fertig: {DIST}\\index.html\n")


def ausliefern(port: int = 8080) -> None:
    import functools
    import http.server
    import socketserver

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    with socketserver.TCPServer(("", port), handler) as server:
        print(f"  Vorschau läuft auf http://localhost:{port}  (Strg+C beendet sie)")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n  Beendet.")


if __name__ == "__main__":
    bericht(bauen())
    if "--serve" in sys.argv:
        ausliefern()
