import numpy as np
from PIL import Image
import pywt

def embed_watermark_dwt(image_path, watermark_path, output_path, alpha=0.1):
    # Încarcă imaginea principală și watermark
    img = Image.open(image_path).convert("L")  # grayscale
    img_array = np.array(img, dtype=float)

    watermark = Image.open(watermark_path).convert("L")
    watermark = watermark.resize((img_array.shape[1]//2, img_array.shape[0]//2))  # resize
    wm_array = np.array(watermark, dtype=float) / 255.0  # normalize 0-1

    # Aplică DWT pe imagine
    coeffs2 = pywt.dwt2(img_array, 'haar')
    LL, (LH, HL, HH) = coeffs2

    # Încorporează watermark în coeficientii LH
    LH_wm = LH + alpha * wm_array
    coeffs2_wm = (LL, (LH_wm, HL, HH))

    # Reconstruiește imaginea watermarked
    watermarked_array = pywt.idwt2(coeffs2_wm, 'haar')
    watermarked_array = np.clip(watermarked_array, 0, 255).astype(np.uint8)

    # Salvează imaginea watermarked
    watermarked_img = Image.fromarray(watermarked_array)
    watermarked_img.save(output_path)
    return output_path