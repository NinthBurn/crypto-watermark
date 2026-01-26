import numpy as np
from PIL import Image
from scipy.fft import dct, idct

class DCTWatermark:
    def __init__(self, block_size=8, coeff_pos=(5, 5)):
        self.block_size = block_size
        self.cx, self.cy = coeff_pos

    # ============================
    #       file load/save
    # ============================
    @staticmethod
    def load_grayscale(path, size=None):
        img = Image.open(path).convert("L")
        if size:
            img = img.resize((size, size), Image.BICUBIC)
        return np.asarray(img, dtype=np.float32)

    @staticmethod
    def load_color(path, size=None):
        img = Image.open(path).convert("RGB")
        if size:
            img = img.resize((size, size), Image.BICUBIC)
        return img

    @staticmethod
    def save_grayscale(array, path):
        array = np.clip(array, 0, 255).astype(np.uint8)
        Image.fromarray(array).save(path)

    @staticmethod
    def save_color(img, path):
        img.save(path)

    # ============================
    #         DCT / IDCT
    # ============================
    def apply_dct(self, channel):
        h, w = channel.shape
        dct_img = np.zeros_like(channel)

        for i in range(0, h, self.block_size):
            for j in range(0, w, self.block_size):
                block = channel[i:i+self.block_size, j:j+self.block_size]
                dct_img[i:i+self.block_size, j:j+self.block_size] = dct(
                    dct(block.T, norm="ortho").T, norm="ortho"
                )
        return dct_img

    def inverse_dct(self, dct_img):
        h, w = dct_img.shape
        img = np.zeros_like(dct_img)

        for i in range(0, h, self.block_size):
            for j in range(0, w, self.block_size):
                block = dct_img[i:i+self.block_size, j:j+self.block_size]
                img[i:i+self.block_size, j:j+self.block_size] = idct(
                    idct(block.T, norm="ortho").T, norm="ortho"
                )
        return img

    # ============================
    #       watermark logic
    # ============================
    def _embed_channel(self, channel, watermark):
        dct_img = self.apply_dct(channel)
        wm = watermark.flatten()
        idx = 0
        h, w = channel.shape

        for i in range(0, h, self.block_size):
            for j in range(0, w, self.block_size):
                if idx >= len(wm):
                    break
                dct_img[i + self.cx, j + self.cy] = wm[idx]
                idx += 1

        return self.inverse_dct(dct_img)

    def _extract_channel(self, channel, wm_shape):
        dct_img = self.apply_dct(channel)
        values = []
        h, w = channel.shape

        for i in range(0, h, self.block_size):
            for j in range(0, w, self.block_size):
                values.append(dct_img[i + self.cx, j + self.cy])

        wm = np.array(values[: wm_shape[0] * wm_shape[1]])
        return wm.reshape(wm_shape)

    # ============================
    #       watermark API
    # ============================
    def embed_grayscale(self, image, watermark):
        return self._embed_channel(image, watermark)

    def extract_grayscale(self, image, wm_shape):
        return self._extract_channel(image, wm_shape)

    def embed_color(self, rgb_img, watermark):
        ycbcr = rgb_img.convert("YCbCr")
        y, cb, cr = ycbcr.split()

        y_arr = np.asarray(y, dtype=np.float32)
        y_wm = self._embed_channel(y_arr, watermark)
        y_wm = np.clip(y_wm, 0, 255).astype(np.uint8)

        return Image.merge(
            "YCbCr",
            (Image.fromarray(y_wm), cb, cr)
        ).convert("RGB")

    def extract_color(self, rgb_img, wm_shape):
        ycbcr = rgb_img.convert("YCbCr")
        y, _, _ = ycbcr.split()
        y_arr = np.asarray(y, dtype=np.float32)
        return self._extract_channel(y_arr, wm_shape)