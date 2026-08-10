(function () {
  "use strict";

  var links = document.querySelectorAll(".galerie-link");
  if (!links.length) return;

  var box = document.createElement("div");
  box.className = "lightbox";
  box.hidden = true;

  var bild = document.createElement("img");
  box.appendChild(bild);

  var schliessen = document.createElement("button");
  schliessen.type = "button";
  schliessen.className = "lightbox-schliessen";
  schliessen.setAttribute("aria-label", "Schließen");
  schliessen.textContent = "×";
  box.appendChild(schliessen);

  document.body.appendChild(box);

  var geoeffnetVon = null;

  function oeffnen(link) {
    var vorschau = link.querySelector("img");
    bild.src = link.getAttribute("href");
    bild.alt = vorschau ? vorschau.alt : "";
    box.hidden = false;
    geoeffnetVon = link;
    schliessen.focus();
  }

  function schliessenFn() {
    box.hidden = true;
    bild.src = "";
    if (geoeffnetVon) geoeffnetVon.focus();
  }

  links.forEach(function (link) {
    link.addEventListener("click", function (ev) {
      ev.preventDefault();
      oeffnen(link);
    });
  });

  box.addEventListener("click", function (ev) {
    if (ev.target === box) schliessenFn();
  });
  schliessen.addEventListener("click", schliessenFn);
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape" && !box.hidden) schliessenFn();
  });
})();
