function previewImage(input, imgElementId) {
  const file = input.files[0];
  if (!file) return;

  const url = URL.createObjectURL(file);
  document.getElementById(imgElementId).src = url;
}

function bindMetricsPreview(inputId, boxId, imgId) {
  const input = document.getElementById(inputId);
  const box = document.getElementById(boxId);
  const img = document.getElementById(imgId);

  box.addEventListener("click", () => input.click());

  input.addEventListener("change", () => {
    const file = input.files[0];
    if (!file) return;

    img.src = URL.createObjectURL(file);
  });
}

function bindPreview(inputId, boxId, imgId) {
  const input = document.getElementById(inputId);
  const box = document.getElementById(boxId);
  const img = document.getElementById(imgId);

  box.addEventListener("click", () => input.click());

  input.addEventListener("change", () => {
    const file = input.files[0];
    if (!file) return;

    img.src = URL.createObjectURL(file);
  });
}


document.getElementById("embed-image").addEventListener("change", e =>
  previewImage(e.target, "embed-image-preview")
);

document.getElementById("embed-watermark").addEventListener("change", e =>
  previewImage(e.target, "embed-watermark-preview")
);


// embed image panels
bindPreview("embed-image", "embed-image-box", "embed-image-preview");
bindPreview("embed-watermark", "embed-watermark-box", "embed-watermark-preview");

// extract image panels
bindPreview("extract-original", "extract-original-box", "extract-original-preview");
bindPreview("extract-watermarked", "extract-watermarked-box", "extract-watermarked-preview");

bindMetricsPreview("metrics-image1", "metrics-image1-box", "metrics-image1-preview");
bindMetricsPreview("metrics-image2", "metrics-image2-box", "metrics-image2-preview");
bindMetricsPreview("metrics-image3", "metrics-image3-box", "metrics-image3-preview");
bindMetricsPreview("metrics-image4", "metrics-image4-box", "metrics-image4-preview");

