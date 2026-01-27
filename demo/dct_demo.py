import matplotlib.pyplot as plt
from PIL import Image
from watermark.dct import DCTWatermark

if __name__ == '__main__':
    block_size = 8
    coeff_pos = (5, 5)
    image_size = 512
    watermark_size = image_size // block_size
    wm = DCTWatermark(block_size, coeff_pos)

    gray = wm.load_grayscale("demo/input/host_image.png", size=image_size)
    color = wm.load_color("demo/input/host_image.png", size=image_size)
    watermark = wm.load_grayscale("demo/input/watermark.png", size=watermark_size)

    gray_wm = wm.embed_grayscale(gray, watermark)
    wm.save_grayscale(gray_wm, "demo/output/gray_watermarked.png")

    gray_reload = wm.load_grayscale("demo/output/gray_watermarked.png")
    gray_rec = wm.extract_grayscale(gray_reload, watermark.shape)
    wm.save_grayscale(gray_rec, "demo/output/gray_recovered.png")

    color_wm = wm.embed_color(color, watermark)
    wm.save_color(color_wm, "demo/output/color_watermarked.png")
    color_rec_mem = wm.extract_color(color_wm, watermark.shape)

    # JPG color
    color_wm.save("demo/output/color_watermarked.jpg", quality=95)
    color_jpg = Image.open("demo/output/color_watermarked.jpg")
    color_rec_jpg = wm.extract_color(color_jpg, watermark.shape)

    # PNG color
    color_wm.save("demo/output/color_watermarked.png")
    color_png = Image.open("demo/output/color_watermarked.png")
    color_rec_png = wm.extract_color(color_png, watermark.shape)

    # memory grayscale
    gray_rec_mem = wm.extract_grayscale(gray_wm, watermark.shape)

    # JPG grayscale
    wm.save_grayscale(gray_wm, "demo/output/gray_watermarked.jpg")
    gray_jpg = wm.load_grayscale("demo/output/gray_watermarked.jpg")
    gray_rec_jpg = wm.extract_grayscale(gray_jpg, watermark.shape)

    # PNG grayscale
    wm.save_grayscale(gray_wm, "demo/output/gray_watermarked.png")
    gray_png = wm.load_grayscale("demo/output/gray_watermarked.png")
    gray_rec_png = wm.extract_grayscale(gray_png, watermark.shape)

    fig, axes = plt.subplots(3, 4, figsize=(18, 12))
    fig.suptitle("DCT Watermarking - Color vs Grayscale / Memory vs JPG vs PNG", fontsize=16)

    # --- input data ---
    axes[0, 0].imshow(color)
    axes[0, 0].set_title("Original Image (Color)")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(gray, cmap="gray")
    axes[0, 1].set_title("Original Image (Grayscale)")
    axes[0, 1].axis("off")

    axes[0, 2].imshow(watermark, cmap="gray")
    axes[0, 2].set_title("Original Watermark")
    axes[0, 2].axis("off")

    axes[0, 3].axis("off")

    # --- color ---
    axes[1, 0].imshow(color_wm)
    axes[1, 0].set_title("Watermarked Color")
    axes[1, 0].axis("off")

    axes[1, 1].imshow(color_rec_mem, cmap="gray")
    axes[1, 1].set_title("Extracted WM (Color / Memory)")
    axes[1, 1].axis("off")

    axes[1, 2].imshow(color_rec_jpg, cmap="gray")
    axes[1, 2].set_title("Extracted WM (Color / JPG)")
    axes[1, 2].axis("off")

    axes[1, 3].imshow(color_rec_png, cmap="gray")
    axes[1, 3].set_title("Extracted WM (Color / PNG)")
    axes[1, 3].axis("off")

    # --- grayscale ---
    axes[2, 0].imshow(gray_wm, cmap="gray")
    axes[2, 0].set_title("Watermarked Grayscale")
    axes[2, 0].axis("off")

    axes[2, 1].imshow(gray_rec_mem, cmap="gray")
    axes[2, 1].set_title("Extracted WM (Gray / Memory)")
    axes[2, 1].axis("off")

    axes[2, 2].imshow(gray_rec_jpg, cmap="gray")
    axes[2, 2].set_title("Extracted WM (Gray / JPG)")
    axes[2, 2].axis("off")

    axes[2, 3].imshow(gray_rec_png, cmap="gray")
    axes[2, 3].set_title("Extracted WM (Gray / PNG)")
    axes[2, 3].axis("off")

    plt.tight_layout()
    plt.show()

