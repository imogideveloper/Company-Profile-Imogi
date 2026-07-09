/**
 * Image cropper untuk Django/Unfold admin.
 * Saat memilih file GAMBAR di form admin, muncul jendela crop (geser/zoom/rasio).
 * File non-gambar (mis. PDF materi) otomatis dilewati.
 */
(function () {
  "use strict";
  if (window.__imogiCropperInit) return;
  window.__imogiCropperInit = true;

  var overlay, imgEl, cropper, currentInput, currentName, currentType;

  function build() {
    overlay = document.createElement("div");
    overlay.className = "imogi-crop-overlay";
    overlay.innerHTML =
      '<div class="imogi-crop-modal">' +
      '  <div class="imogi-crop-head"><span>Atur Gambar</span>' +
      '    <button type="button" class="imogi-crop-x" data-act="cancel">&times;</button></div>' +
      '  <div class="imogi-crop-stage"><img class="imogi-crop-img" alt=""></div>' +
      '  <div class="imogi-crop-tools">' +
      '    <div class="imogi-crop-ratios">' +
      '      <button type="button" data-ratio="NaN" class="active">Bebas</button>' +
      '      <button type="button" data-ratio="1.7778">16:9</button>' +
      '      <button type="button" data-ratio="1.3333">4:3</button>' +
      '      <button type="button" data-ratio="1">1:1</button>' +
      '      <button type="button" data-act="rotate" title="Putar">&#8635;</button>' +
      '    </div>' +
      '    <div class="imogi-crop-actions">' +
      '      <button type="button" class="imogi-crop-cancel" data-act="cancel">Batal</button>' +
      '      <button type="button" class="imogi-crop-apply" data-act="apply">Terapkan</button>' +
      '    </div>' +
      '  </div>' +
      "</div>";
    document.body.appendChild(overlay);
    imgEl = overlay.querySelector(".imogi-crop-img");

    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) { close(); return; }
      var el = e.target.closest("[data-act],[data-ratio]");
      if (!el) return;
      if (el.hasAttribute("data-ratio")) {
        overlay.querySelectorAll("[data-ratio]").forEach(function (b) { b.classList.remove("active"); });
        el.classList.add("active");
        if (cropper) cropper.setAspectRatio(parseFloat(el.getAttribute("data-ratio")));
        return;
      }
      var act = el.getAttribute("data-act");
      if (act === "cancel") close();
      else if (act === "rotate" && cropper) cropper.rotate(90);
      else if (act === "apply") apply();
    });
  }

  function open(input, file) {
    if (typeof Cropper === "undefined") return;
    if (!overlay) build();
    currentInput = input;
    currentName = file.name;
    currentType = file.type === "image/png" ? "image/png" : "image/jpeg";
    if (cropper) { cropper.destroy(); cropper = null; }
    imgEl.src = URL.createObjectURL(file);
    overlay.querySelectorAll("[data-ratio]").forEach(function (b, i) {
      b.classList.toggle("active", i === 0);
    });
    overlay.classList.add("open");
    document.body.style.overflow = "hidden";
    imgEl.onload = function () {
      cropper = new Cropper(imgEl, {
        viewMode: 1, autoCropArea: 1, background: false,
        dragMode: "move", movable: true, zoomable: true, responsive: true
      });
    };
  }

  function apply() {
    if (!cropper) return close();
    var canvas = cropper.getCroppedCanvas({ maxWidth: 1600, maxHeight: 1600, imageSmoothingQuality: "high" });
    canvas.toBlob(function (blob) {
      if (!blob) return close();
      var ext = currentType === "image/png" ? ".png" : ".jpg";
      var base = (currentName || "gambar").replace(/\.[^.]+$/, "");
      var f = new File([blob], base + ext, { type: currentType });
      try {
        var dt = new DataTransfer();
        dt.items.add(f);
        currentInput.files = dt.files;
        currentInput.dataset.imogiCropped = "1";
        currentInput.dispatchEvent(new Event("change", { bubbles: true }));
      } catch (err) { /* browser lama tak dukung DataTransfer */ }
      close();
    }, currentType, 0.9);
  }

  function close() {
    if (overlay) overlay.classList.remove("open");
    document.body.style.overflow = "";
    if (cropper) { cropper.destroy(); cropper = null; }
    currentInput = null;
  }

  document.addEventListener("change", function (e) {
    var input = e.target;
    if (!input || input.tagName !== "INPUT" || input.type !== "file") return;
    if (input.dataset.imogiCropped) { delete input.dataset.imogiCropped; return; }
    var file = input.files && input.files[0];
    if (!file || !file.type || file.type.indexOf("image/") !== 0) return;
    open(input, file);
  }, true);
})();
