# controller/image_record_controller.py
import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import numpy as np
from starlette.responses import FileResponse
from PIL import Image

from model.image_record import ImageRecord
from service.image_record_service import ImageRecordService
from repository.image_record_repo import ImageRecordRepository
from watermarking.DCT import DCTWatermark
from watermarking.hybrid import HybridWatermark
from watermarking.attacks import ImageAttacks

router = APIRouter()
repository = ImageRecordRepository()
service = ImageRecordService(repository)

UPLOAD_DIR = "uploadedImages"
os.makedirs(UPLOAD_DIR, exist_ok=True)

from fastapi.responses import FileResponse

@router.post("/images/upload/", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    watermark_file: UploadFile = File(...),
    method: str = Form(...),
    format: str = Form(...),
    image_size: int = Form(...),
    watermark_size: int = Form(...),
    dct_block_size: int = Form(...),
    dct_coeffs: int = Form(...),
    is_image_colored: bool = Form(...)
):
    # Salvare locală
    global watermarked_path
    image_path = os.path.join(UPLOAD_DIR, file.filename)
    wm_path = os.path.join(UPLOAD_DIR, watermark_file.filename)

    with open(image_path, "wb") as f:
        f.write(await file.read())
    with open(wm_path, "wb") as f:
        f.write(await watermark_file.read())

    method = method.upper()

    try:
        image_size = image_size if image_size > 0 else 512
        watermark_size = watermark_size if watermark_size > 0 else 32
        dct_block_size = dct_block_size if dct_block_size > 0 else 8
        dct_coeffs = dct_coeffs if dct_coeffs > 0 else 5
        
        match method:
            case "DWT":
                print("in controller dwt")
                record, watermarked_path = service.create_image(
                    filename=file.filename,
                    method=method,
                    image_path=image_path,
                    watermark_path=wm_path,
                    format=file.content_type
                )

            case "DCT":
                watermarked_path = os.path.join(UPLOAD_DIR, f"watermarked_{file.filename}")
                watermark_size = image_size // dct_block_size
                wm = DCTWatermark(dct_block_size, (dct_coeffs, dct_coeffs))
                
                if is_image_colored:
                    original_image = wm.load_color(image_path, size=image_size)
                    watermark = wm.load_grayscale(wm_path, size=watermark_size)
                    embedded = wm.embed_color(original_image, watermark)
                    wm.save_color(embedded, watermarked_path)
                else:
                    original_image = wm.load_grayscale(image_path, size=image_size)
                    watermark = wm.load_grayscale(wm_path, size=watermark_size)
                    embedded = wm.embed_grayscale(original_image, watermark)
                    wm.save_grayscale(embedded, watermarked_path)
                
            case "HYBRID":
                wm = HybridWatermark(block_size=dct_block_size, coeff_pos=(dct_coeffs, dct_coeffs), alpha=15.0, image_size=image_size)
                watermarked_path = os.path.join(UPLOAD_DIR, f"watermarked_{file.filename}")
                wm.embed(image_path, wm_path, watermarked_path)
                
            case _:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported watermarking method"
                )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Returnează și imaginea watermarked
    return FileResponse(
        watermarked_path,
        media_type=file.content_type,
        filename=f"watermarked_{file.filename}"
    )

@router.post("/images/extract-watermark/", response_model=dict)
async def extract_watermark(
    original_image: UploadFile = File(...),
    watermarked_image: UploadFile = File(...),
    method: str = Form(...),
    format: str = Form(...),
    image_size: int = Form(...),
    watermark_size: int = Form(...),
    dct_block_size: int = Form(...),
    dct_coeffs: int = Form(...),
    is_image_colored: bool = Form(...),
    attack_type: str = Form(None),       # "NOISE", "BLUR", "JPEG"
    attack_param: float = Form(None)     # attack intensity
):
    # Salvare locală
    global extracted_path
    orig_path = os.path.join(UPLOAD_DIR, "orig_" + original_image.filename)
    wm_path = os.path.join(UPLOAD_DIR, "wm_" + watermarked_image.filename)

    with open(orig_path, "wb") as f:
        f.write(await original_image.read())
    with open(wm_path, "wb") as f:
        f.write(await watermarked_image.read())

    method = method.upper()
    extracted_path = os.path.join(UPLOAD_DIR, "extracted_" + original_image.filename)

    attacked_path = wm_path
    if attack_type:
        attacked_path = os.path.join(
            UPLOAD_DIR,
            f"attacked_{watermarked_image.filename}"
        )

        match attack_type.upper():
            case "NOISE":
                ImageAttacks.gaussian_noise(
                    image_path=wm_path,
                    output_path=attacked_path,
                    var=attack_param or 10
                )
            case "BLUR":
                ImageAttacks.gaussian_blur(
                    image_path=wm_path,
                    output_path=attacked_path,
                    radius=attack_param or 2
                )
            case "JPEG":
                ImageAttacks.jpeg_compression(
                    image_path=wm_path,
                    output_path=attacked_path,
                    quality=int(attack_param or 30)
                )
            case _:
                raise HTTPException(400, detail="Unsupported attack type")

    try:
        match method:
            case "DWT":
                extracted_wm = service.extract_watermark_dwt(
                    original_path=orig_path,
                    watermarked_path=attacked_path
                )
                service.save_extracted_watermark(extracted_wm, extracted_path)

            case "DCT":
                watermark_size = image_size // dct_block_size
                wm = DCTWatermark(dct_block_size, (dct_coeffs, dct_coeffs))

                if is_image_colored:
                    image = wm.load_color(attacked_path, size=image_size)
                    extracted_watermark = wm.extract_color(image, (watermark_size, watermark_size))
                    wm.save_grayscale(extracted_watermark, extracted_path)
                else:
                    image = wm.load_grayscale(attacked_path, size=image_size)
                    extracted_watermark = wm.extract_grayscale(image, (watermark_size, watermark_size))
                    wm.save_grayscale(extracted_watermark, extracted_path)

            case "HYBRID":
                wm = HybridWatermark(block_size=dct_block_size, coeff_pos=(dct_coeffs, dct_coeffs), alpha=15.0, image_size=image_size)
                extracted_img = wm.extract(attacked_path, wm_shape=(watermark_size, watermark_size))
                extracted_img.save(extracted_path)

            case _:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported extraction method"
                )

    except ValueError as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(
        extracted_path,
        media_type=original_image.content_type,
        filename=f"extracted_{original_image.filename}"
    )

def compute_psnr(orig, recon):
    mse = np.mean((orig - recon) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10((255.0 ** 2) / mse)

def compute_ber(orig_wm, extr_wm):
    orig_bin = (orig_wm > 127).astype(int)
    extr_bin = (extr_wm > 127).astype(int)
    return np.sum(orig_bin != extr_bin) / orig_bin.size

@router.post("/images/metrics/", response_model=dict)
async def compute_metrics(
    original_image: UploadFile = File(...),
    watermarked_image: UploadFile = File(...),
    original_watermark: UploadFile = File(...),
    extracted_watermark: UploadFile = File(...)
):
    try:
        # Save uploads
        paths = {}
        for name, file in zip(
            ["orig", "wm_img", "orig_wm", "extr_wm"],
            [original_image, watermarked_image, original_watermark, extracted_watermark]
        ):
            path = os.path.join(UPLOAD_DIR, f"{name}_{file.filename}")
            with open(path, "wb") as f:
                f.write(await file.read())
            paths[name] = path

        orig_img = Image.open(paths["orig"])
        wm_img = Image.open(paths["wm_img"])

        if orig_img.mode != "L":
            orig_img = orig_img.convert("L")
        if wm_img.mode != "L":
            wm_img = wm_img.convert("L")

        # Rescale original image to watermarked size if necessary
        if orig_img.size != wm_img.size:
            orig_img = orig_img.resize(wm_img.size, Image.BICUBIC)

        orig_img_np = np.array(orig_img, dtype=np.uint8)
        wm_img_np = np.array(wm_img, dtype=np.uint8)

        orig_wm = np.array(Image.open(paths["orig_wm"]).convert("L"), dtype=np.uint8)
        extr_wm = np.array(Image.open(paths["extr_wm"]).convert("L"), dtype=np.uint8)

        # Rescale original watermark to extracted watermark size
        if orig_wm.shape != extr_wm.shape:
            orig_wm = np.array(
                Image.fromarray(orig_wm).resize(
                    (extr_wm.shape[1], extr_wm.shape[0]), Image.BICUBIC
                ),
                dtype=np.uint8
            )

        psnr_val = compute_psnr(orig_img_np, wm_img_np)
        ber_val = compute_ber(orig_wm, extr_wm)
        return {"psnr": psnr_val, "ber": ber_val}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
