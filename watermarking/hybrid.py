import numpy as np
from PIL import Image
import pywt
from scipy.fft import dct, idct


class HybridWatermark:
    def __init__(self, block_size=8, coeff_pos=(4, 4), alpha=15.0, image_size=512):
        self.block_size = block_size
        self.cx, self.cy = coeff_pos
        self.alpha = alpha
        self.image_size = image_size

    def apply_dct_block(self, block):
        return dct(dct(block.T, norm="ortho").T, norm="ortho")

    def inverse_dct_block(self, block):
        return idct(idct(block.T, norm="ortho").T, norm="ortho")

    def embed(self, image_path, watermark_path, output_path):

        img = Image.open(image_path).resize((self.image_size, self.image_size), Image.Resampling.BICUBIC)

        is_rgb = img.mode == "RGB"
        if is_rgb:
            ycbcr = img.convert("YCbCr")
            y, cb, cr = ycbcr.split()
            channel = np.array(y, dtype=np.float32)
        else:
            channel = np.array(img.convert("L"), dtype=np.float32)

        # DWT
        LL, (LH, HL, HH) = pywt.dwt2(channel, 'haar')

        num_blocks_h = LH.shape[0] // self.block_size
        num_blocks_w = LH.shape[1] // self.block_size

        watermark = Image.open(watermark_path).convert("L")
        watermark = watermark.resize((num_blocks_w, num_blocks_h), Image.Resampling.BICUBIC)
        wm = (np.array(watermark) > 127).astype(np.int32)  # 0 sau 1

        for i in range(num_blocks_h):
            for j in range(num_blocks_w):
                block = LH[i * self.block_size:(i + 1) * self.block_size, j * self.block_size:(j + 1) * self.block_size]
                dct_block = self.apply_dct_block(block)
                dct_block[self.cx, self.cy] += self.alpha * (2 * wm[i, j] - 1)
                LH[i * self.block_size:(i + 1) * self.block_size,
                j * self.block_size:(j + 1) * self.block_size] = self.inverse_dct_block(dct_block)

        watermarked_channel = pywt.idwt2((LL, (LH, HL, HH)), 'haar')
        watermarked_channel = np.clip(watermarked_channel, 0, 255).astype(np.uint8)

        if is_rgb:
            y_wm = Image.fromarray(watermarked_channel)
            out_img = Image.merge("YCbCr", (y_wm, cb, cr)).convert("RGB")
        else:
            out_img = Image.fromarray(watermarked_channel)

        out_img.save(output_path)

    def extract(self, watermarked_path, wm_shape):

        img = Image.open(watermarked_path).resize((self.image_size, self.image_size), Image.Resampling.BICUBIC)

        if img.mode == "RGB":
            y = img.convert("YCbCr").split()[0]
            channel = np.array(y, dtype=np.float32)
        else:
            channel = np.array(img.convert("L"), dtype=np.float32)

        # DWT
        _, (LH, _, _) = pywt.dwt2(channel, 'haar')

        num_blocks_h = LH.shape[0] // self.block_size
        num_blocks_w = LH.shape[1] // self.block_size

        extracted = np.zeros((num_blocks_h, num_blocks_w), dtype=np.int32)
        for i in range(num_blocks_h):
            for j in range(num_blocks_w):
                block = LH[i * self.block_size:(i + 1) * self.block_size, j * self.block_size:(j + 1) * self.block_size]
                dct_block = self.apply_dct_block(block)
                # Thresholding pentru a decide 0 sau 1
                extracted[i, j] = 1 if dct_block[self.cx, self.cy] > 0 else 0

        # Scale la 0-255
        wm_img = (extracted * 255).astype(np.uint8)
        wm_img = Image.fromarray(wm_img).resize(wm_shape, Image.Resampling.BICUBIC)
        return wm_img
