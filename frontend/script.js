const server = 'http://localhost:8000';

function getEmbedOptions() {
  return {
    method: document.querySelector('input[name="embed-method"]:checked').value,
    format: document.querySelector('input[name="embed-format"]:checked').value,
    imageSize: Number(document.getElementById('image-size').value),
    watermarkSize: Number(document.getElementById('watermark-size').value),
    dctBlockSize: Number(document.getElementById('dct-block-size').value),
    dctCoeffs: Number(document.getElementById('dct-coeffs').value),
    coloredImage: document.getElementById('colored-image').checked,
    attackType: document.getElementById('attack-type').value,
    attackParam: document.getElementById('attack-param').value
  };
}

function getFormDataWithOptions() {
  const formData = new FormData();
  const options = getEmbedOptions();
  formData.append('method', options.method);
  formData.append('format', options.format);
  formData.append('image_size', options.imageSize);
  formData.append('watermark_size', options.watermarkSize);
  formData.append('dct_block_size', options.dctBlockSize);
  formData.append('dct_coeffs', options.dctCoeffs);
  formData.append('is_image_colored', options.coloredImage);

  return formData;
}

function getExtractFormDataWithOptions() {
  const formData = getFormDataWithOptions();
  const options = getEmbedOptions();

  if (options.attackType) {
    formData.append('attack_type', options.attackType);

    if (options.attackParam) {
      formData.append('attack_param', options.attackParam.toString());
    }
  }

  return formData;
}


document.getElementById('embed-btn').addEventListener('click', () => {
  const options = getEmbedOptions();
  console.log(options);
});


document.getElementById('embed-btn').addEventListener('click', async () => {
  const image = document.getElementById('embed-image').files[0];
  const watermark = document.getElementById('embed-watermark').files[0];

  if (!image || !watermark) {
    alert('Please select both image and watermark.');
    return;
  }

  const formData = getFormDataWithOptions();
  formData.append('file', image);
  formData.append('watermark_file', watermark);

  const response = await fetch(`${server}/images/upload`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    alert('Embedding failed');
    return;
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);

  document.getElementById('embed-result').src = url;
});

document.getElementById('extract-btn').addEventListener('click', async () => {
  const original = document.getElementById('extract-original').files[0];
  const watermarked = document.getElementById('extract-watermarked').files[0];

  if (!original || !watermarked) {
    alert('Please select both images.');
    return;
  }

  const formData = getExtractFormDataWithOptions();
  formData.append('original_image', original);
  formData.append('watermarked_image', watermarked);

  try {
    const response = await fetch(`${server}/images/extract-watermark`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      alert('Extraction failed');
      return;
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    document.getElementById('extract-result').src = url;

  } catch (err) {
    console.error(err);
    alert('Server error during extraction');
  }
});

document.getElementById("metrics-btn").addEventListener("click", async () => {
  const files = [
    document.getElementById("metrics-image1").files[0],
    document.getElementById("metrics-image2").files[0],
    document.getElementById("metrics-image3").files[0],
    document.getElementById("metrics-image4").files[0]
  ];

  if (files.some(f => !f)) {
    alert("Please upload all 4 images.");
    return;
  }

  const formData = new FormData();
  formData.append('original_image', files[0]);
  formData.append('watermarked_image', files[1]);
  formData.append('original_watermark', files[2]);
  formData.append('extracted_watermark', files[3]);
  
  const response = await fetch(`${server}/images/metrics`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    alert("Metrics computation failed");
    return;
  }

  const data = await response.json();
  document.getElementById("psnr-value").textContent = data.psnr;
  document.getElementById("ber-value").textContent = data.ber;
});
