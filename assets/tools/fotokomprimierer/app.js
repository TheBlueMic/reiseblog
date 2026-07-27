// Fotokomprimierer: verkleinert und komprimiert Fotos direkt im Browser,
// auf das Format, das build.py im Reiseblog-Repo ohnehin erzeugt
// (siehe site.config.json: image_widths, image_quality).
(function () {
  "use strict";

  const MAX_WIDTH = 1600; // = groesster Wert aus site.config.json -> image_widths
  let qualitaet = 0.82;   // = site.config.json -> image_quality / 100

  const eingabe = document.getElementById("datei-eingabe");
  const qualitaetRegler = document.getElementById("qualitaet-regler");
  const qualitaetWert = document.getElementById("qualitaet-wert");
  const fortschrittZeile = document.getElementById("fortschritt-zeile");
  const ergebnisse = document.getElementById("ergebnisse");
  const zipKnopf = document.getElementById("zip-knopf");
  const resetKnopf = document.getElementById("reset-knopf");
  const gesamtZeile = document.getElementById("gesamt-zeile");
  const nichtUnterstuetzt = document.getElementById("nicht-unterstuetzt");

  let ergebnisListe = []; // {name, originalSize, compressedSize, blob}
  let laeuft = false;

  function unterstuetzt() {
    return typeof window.createImageBitmap === "function" &&
           typeof HTMLCanvasElement.prototype.toBlob === "function";
  }

  if (!unterstuetzt()) {
    nichtUnterstuetzt.style.display = "block";
    eingabe.disabled = true;
    qualitaetRegler.disabled = true;
    return;
  }

  qualitaetRegler.addEventListener("input", () => {
    qualitaet = Number(qualitaetRegler.value) / 100;
    qualitaetWert.textContent = qualitaetRegler.value;
  });

  function formatiereGroesse(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(0) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }

  function eindeutigerName(name, bisherige) {
    if (!bisherige.has(name)) return name;
    const punkt = name.lastIndexOf(".");
    const stamm = punkt === -1 ? name : name.slice(0, punkt);
    const endung = punkt === -1 ? "" : name.slice(punkt);
    let zaehler = 2;
    let kandidat = `${stamm} (${zaehler})${endung}`;
    while (bisherige.has(kandidat)) {
      zaehler += 1;
      kandidat = `${stamm} (${zaehler})${endung}`;
    }
    return kandidat;
  }

  function karteAnlegen() {
    const karte = document.createElement("div");
    karte.className = "karte";
    const bild = document.createElement("img");
    const info = document.createElement("div");
    karte.appendChild(bild);
    karte.appendChild(info);
    ergebnisse.appendChild(karte);
    return { karte, bild, info };
  }

  function karteFehler(info, name, meldung) {
    info.innerHTML = "";
    const nameZeile = document.createElement("div");
    nameZeile.className = "name";
    nameZeile.textContent = name;
    const fehlerZeile = document.createElement("div");
    fehlerZeile.className = "fehler";
    fehlerZeile.textContent = meldung;
    info.appendChild(nameZeile);
    info.appendChild(fehlerZeile);
  }

  function karteErfolg(bild, info, name, originalGroesse, komprimiertGroesse, url) {
    bild.src = url;
    info.innerHTML = "";
    const nameZeile = document.createElement("div");
    nameZeile.className = "name";
    nameZeile.textContent = name;
    const groesseZeile = document.createElement("div");
    groesseZeile.className = "groesse";
    const prozent = originalGroesse > 0
      ? Math.round((1 - komprimiertGroesse / originalGroesse) * 100)
      : 0;
    const vorzeichen = prozent >= 0 ? "-" : "+";
    groesseZeile.textContent =
      `vorher: ${formatiereGroesse(originalGroesse)} → nachher: ` +
      `${formatiereGroesse(komprimiertGroesse)} (${vorzeichen}${Math.abs(prozent)}%)`;
    const link = document.createElement("a");
    link.className = "download";
    link.href = url;
    link.download = name;
    link.textContent = "Herunterladen";
    info.appendChild(nameZeile);
    info.appendChild(groesseZeile);
    info.appendChild(link);
  }

  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");

  async function fotoVerarbeiten(datei) {
    const bitmap = await createImageBitmap(datei, { imageOrientation: "from-image" });
    try {
      const zielBreite = Math.min(MAX_WIDTH, bitmap.width);
      const zielHoehe = Math.round(bitmap.height * (zielBreite / bitmap.width));
      canvas.width = zielBreite;
      canvas.height = zielHoehe;
      ctx.imageSmoothingQuality = "high";
      ctx.clearRect(0, 0, zielBreite, zielHoehe);
      ctx.drawImage(bitmap, 0, 0, zielBreite, zielHoehe);
      const blob = await new Promise((resolve) =>
        canvas.toBlob(resolve, "image/jpeg", qualitaet)
      );
      return blob;
    } finally {
      bitmap.close();
    }
  }

  async function batchVerarbeiten(dateien) {
    laeuft = true;
    zipKnopf.disabled = true;
    const bisherigeNamen = new Set(ergebnisListe.map((e) => e.name));
    const bilddateien = dateien.filter((d) => d.type.startsWith("image/"));
    const uebersprungen = dateien.length - bilddateien.length;
    if (uebersprungen > 0) {
      fortschrittZeile.textContent =
        `${uebersprungen} Datei(en) übersprungen, kein Bildformat.`;
    }

    for (let i = 0; i < bilddateien.length; i += 1) {
      const datei = bilddateien[i];
      fortschrittZeile.textContent =
        `Verarbeite Bild ${i + 1} von ${bilddateien.length} …`;
      const { bild, info } = karteAnlegen();
      const name = eindeutigerName(datei.name, bisherigeNamen);
      bisherigeNamen.add(name);
      try {
        const blob = await fotoVerarbeiten(datei);
        const url = URL.createObjectURL(blob);
        karteErfolg(bild, info, name, datei.size, blob.size, url);
        ergebnisListe.push({
          name,
          originalSize: datei.size,
          compressedSize: blob.size,
          blob,
        });
      } catch (fehler) {
        karteFehler(info, name,
          "Dieses Format wird vom Browser nicht unterstützt (z. B. HEIC) " +
          "oder die Datei ist beschädigt.");
      }
    }

    fortschrittZeile.textContent = "Fertig.";
    laeuft = false;
    zipKnopf.disabled = ergebnisListe.length === 0;
    gesamtAnzeigen();
  }

  function gesamtAnzeigen() {
    if (ergebnisListe.length === 0) {
      gesamtZeile.textContent = "";
      return;
    }
    const vorSumme = ergebnisListe.reduce((s, e) => s + e.originalSize, 0);
    const nachSumme = ergebnisListe.reduce((s, e) => s + e.compressedSize, 0);
    gesamtZeile.textContent =
      `Gesamt: ${ergebnisListe.length} Fotos, ` +
      `${formatiereGroesse(vorSumme)} → ${formatiereGroesse(nachSumme)}`;
  }

  eingabe.addEventListener("change", (ereignis) => {
    const dateien = Array.from(ereignis.target.files || []);
    eingabe.value = ""; // erlaubt erneute Auswahl derselben Datei(en)
    if (dateien.length === 0 || laeuft) return;
    batchVerarbeiten(dateien);
  });

  zipKnopf.addEventListener("click", async () => {
    if (ergebnisListe.length === 0) return;
    zipKnopf.disabled = true;
    fortschrittZeile.textContent = "ZIP wird erstellt …";
    const zip = new JSZip();
    ergebnisListe.forEach((eintrag) => zip.file(eintrag.name, eintrag.blob));
    const zipBlob = await zip.generateAsync({ type: "blob", compression: "STORE" });
    const zeitstempel = new Date()
      .toISOString()
      .replace(/[-:]/g, "")
      .replace("T", "-")
      .slice(0, 13);
    const zipUrl = URL.createObjectURL(zipBlob);
    const link = document.createElement("a");
    link.href = zipUrl;
    link.download = `fotos-komprimiert-${zeitstempel}.zip`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(zipUrl);
    fortschrittZeile.textContent = "Fertig.";
    zipKnopf.disabled = false;
  });

  resetKnopf.addEventListener("click", () => {
    ergebnisListe.forEach((eintrag) => {
      // Objekt-URLs der Vorschaubilder wieder freigeben.
      const bilder = ergebnisse.querySelectorAll("img");
      bilder.forEach((bild) => URL.revokeObjectURL(bild.src));
    });
    ergebnisListe = [];
    ergebnisse.innerHTML = "";
    fortschrittZeile.textContent = "";
    gesamtZeile.textContent = "";
    zipKnopf.disabled = true;
  });
})();
