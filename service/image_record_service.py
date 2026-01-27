from typing import Any

import numpy as np
from PIL import Image
import pywt

from model.image_record import ImageRecord


class ImageRecordService:

    def __init__(self, repository):
        self.repository = repository

    def create_image(self, filename: str, method: str, image_path: str, watermark_path: str, format: str) -> tuple[
        ImageRecord, Any]:

        # Deschide imaginea originală
        img = Image.open(image_path).convert("L")
        width, height = img.size
        # format = img.format  # PNG sau JPEG
        print(format)
        # Verifică format și dimensiuni
        format = format.lower()
        if format not in ["image/png", "image/jpeg"]:
            raise ValueError(f"Image format not supported: {format}")
        if width < 256 or height < 256:
            raise ValueError("Image too small")
        if width > 1024 or height > 1024:
            raise ValueError("Image too large")

        # Aplică metoda de watermarking (doar DWT pentru exemplu)
        if method.upper() == "DWT":
            watermarked_path, extracted_wm_array = self.embed_watermark_dwt(image_path, watermark_path)
        else:
            raise ValueError(f"Method {method} not supported yet")

        # Calculează metrici
        psnr = self.calculate_psnr(image_path, watermarked_path)
        ber = self.calculate_ber(watermark_path, extracted_wm_array)

        # Salvează în DB prin repository
        self.repository.create(filename, method, psnr, ber, width, height, format)

        # Returnează obiect ImageRecord
        record = ImageRecord(filename, method, psnr, ber, width, height, format)
        return record, watermarked_path

    # --- Funcții de watermarking și metrici ---

    def embed_watermark_dwt(self, image_path, watermark_path, alpha=0.1):
        img = Image.open(image_path).convert("L")
        img_array = np.array(img, dtype=float)

        coeffs2 = pywt.dwt2(img_array, 'haar')
        LL, (LH, HL, HH) = coeffs2

        watermark = Image.open(watermark_path).convert("L")
        watermark = watermark.resize((LH.shape[1], LH.shape[0]))
        wm_array = np.array(watermark, dtype=float) / 255.0

        LH_wm = LH + alpha * wm_array
        coeffs2_wm = (LL, (LH_wm, HL, HH))

        watermarked_array = pywt.idwt2(coeffs2_wm, 'haar')
        watermarked_array = np.clip(watermarked_array, 0, 255).astype(np.uint8)

        watermarked_img = Image.fromarray(watermarked_array)
        watermarked_path = image_path.replace(".", "_wm.")
        watermarked_img.save(watermarked_path)
        print("LH shape:", LH.shape)
        print("Watermark shape:", wm_array.shape)

        return watermarked_path, wm_array

    def extract_watermark_dwt(self, original_path, watermarked_path, alpha=0.1):

        orig = np.array(Image.open(original_path).convert("L"), dtype=float)
        wm = np.array(Image.open(watermarked_path).convert("L"), dtype=float)

        if orig.shape != wm.shape:
            raise ValueError("Original image and watermarked image must have the same size")

        LL_o, (LH_o, _, _) = pywt.dwt2(orig, 'haar')
        LL_w, (LH_w, _, _) = pywt.dwt2(wm, 'haar')

        extracted_wm = (LH_w - LH_o) / alpha

        # normalizare robustă
        extracted_wm = (extracted_wm - extracted_wm.min()) / (extracted_wm.max() - extracted_wm.min())

        return extracted_wm

    def save_extracted_watermark(self, extracted_wm_array, output_path):

        wm_img = (extracted_wm_array * 255).astype(np.uint8)
        Image.fromarray(wm_img).save(output_path)

    def calculate_psnr(self, original_path, watermarked_path):
        img1 = np.array(Image.open(original_path).convert("L"), dtype=float)
        img2 = np.array(Image.open(watermarked_path).convert("L"), dtype=float)
        mse = np.mean((img1 - img2) ** 2)
        if mse == 0:
            return float('inf')
        max_pixel = 255.0
        return 20 * np.log10(max_pixel / np.sqrt(mse))

    def calculate_ber(self, original_wm_path, extracted_wm_array):
        original_wm = Image.open(original_wm_path).convert("L")
        original_wm = original_wm.resize(
            (extracted_wm_array.shape[1], extracted_wm_array.shape[0])
        )

        original_wm = np.array(original_wm, dtype=float) / 255.0

        original_bits = (original_wm > 0.5).astype(int)
        extracted_bits = (extracted_wm_array > 0.5).astype(int)

        return np.sum(original_bits != extracted_bits) / original_bits.size