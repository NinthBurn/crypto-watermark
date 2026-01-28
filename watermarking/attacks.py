import numpy as np
from PIL import Image, ImageFilter
import io


class ImageAttacks:

    @staticmethod
    def gaussian_noise(image_path, output_path, mean=0.0, var=10.0):
        img = Image.open(image_path).convert("L")
        img_np = np.array(img, dtype=np.float32)

        sigma = var ** 0.5
        noise = np.random.normal(mean, sigma, img_np.shape)

        noisy = img_np + noise
        noisy = np.clip(noisy, 0, 255).astype(np.uint8)

        Image.fromarray(noisy).save(output_path)

    @staticmethod
    def gaussian_blur(image_path, output_path, radius=2):
        img = Image.open(image_path)
        blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
        blurred.save(output_path)

    @staticmethod
    def jpeg_compression(image_path, output_path, quality=30):
        img = Image.open(image_path)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)

        compressed = Image.open(buffer)
        compressed.save(output_path)
