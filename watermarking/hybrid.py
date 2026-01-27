import numpy as np
from PIL import Image
import pywt
from scipy.fft import dct, idct


class HybridWatermark:
    def __init__(self, block_size=8, coeff_pos=(4, 4), alpha=15.0):
        self.block_size = block_size
        self.cx, self.cy = coeff_pos
        self.alpha = alpha

    def apply_dct_block(self, block):
        return dct(dct(block.T, norm="ortho").T, norm="ortho")

    def inverse_dct_block(self, block):
        return idct(idct(block.T, norm="ortho").T, norm="ortho")

    def embed(self, image_path, watermark_path, output_path):

        img = Image.open(image_path)

        if img.mode == "RGB":
            ycbcr = img.convert("YCbCr")
            y, cb, cr = ycbcr.split()
            channel = np.array(y, dtype=np.float32)

        else:
            channel = np.array(img.convert("L"), dtype=np.float32)

        #  DWT
        LL, (LH, HL, HH) = pywt.dwt2(channel, 'haar')

        num_blocks_h = LH.shape[0] // self.block_size
        num_blocks_w = LH.shape[1] // self.block_size

        # watermark
        watermark = Image.open(watermark_path).convert("L")
        watermark = watermark.resize((num_blocks_w, num_blocks_h))
        wm = np.array(watermark, dtype=np.float32).flatten() / 255.0

        # DCT embedding
        idx = 0
        for i in range(0, num_blocks_h * self.block_size, self.block_size):
            for j in range(0, num_blocks_w * self.block_size, self.block_size):

                if idx >= len(wm):
                    break

                block = LH[i:i + self.block_size, j:j + self.block_size]
                dct_block = self.apply_dct_block(block)

                dct_block[self.cx, self.cy] += self.alpha * wm[idx]

                LH[i:i + self.block_size, j:j + self.block_size] = \
                    self.inverse_dct_block(dct_block)

                idx += 1

        # IDWT
        watermarked_channel = pywt.idwt2((LL, (LH, HL, HH)), 'haar')
        watermarked_channel = np.clip(watermarked_channel, 0, 255).astype(np.uint8)

        if img.mode == "RGB":
            y_wm = Image.fromarray(watermarked_channel)
            out_img = Image.merge("YCbCr", (y_wm, cb, cr)).convert("RGB")
        else:
            out_img = Image.fromarray(watermarked_channel)

        out_img.save(output_path)

    def extract(self, watermarked_path, wm_shape):

        img = Image.open(watermarked_path)

        if img.mode == "RGB":
            y = img.convert("YCbCr").split()[0]
            channel = np.array(y, dtype=np.float32)
        else:
            channel = np.array(img.convert("L"), dtype=np.float32)

        # DWT
        _, (LH, _, _) = pywt.dwt2(channel, 'haar')

        extracted = []

        num_blocks_h = LH.shape[0] // self.block_size
        num_blocks_w = LH.shape[1] // self.block_size

        for i in range(0, num_blocks_h * self.block_size, self.block_size):
            for j in range(0, num_blocks_w * self.block_size, self.block_size):

                block = LH[i:i + self.block_size, j:j + self.block_size]
                dct_block = self.apply_dct_block(block)

                val = dct_block[self.cx, self.cy] / self.alpha
                extracted.append(val)

        wm = np.array(extracted[: wm_shape[0] * wm_shape[1]])
        wm = wm.reshape(wm_shape)

        wm = np.clip(wm * 255, 0, 255).astype(np.uint8)
        return wm
