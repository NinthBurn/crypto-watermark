# controller/image_record_controller.py
import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from service.image_record_service import ImageRecordService
from repository.image_record_repo import ImageRecordRepository

router = APIRouter()
repository = ImageRecordRepository()
service = ImageRecordService(repository)

UPLOAD_DIR = "uploadedImages"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/images/upload/", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    watermark_file: UploadFile = File(...),
    method: str = Form(...)
):
    print(file.content_type)
    # Verifică format imagine
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Image must be PNG or JPEG controller")
    if watermark_file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Watermark must be PNG or JPEG controller")

    # Salvează fișierele local
    image_path = os.path.join(UPLOAD_DIR, file.filename)
    wm_path = os.path.join(UPLOAD_DIR, watermark_file.filename)

    with open(image_path, "wb") as f:
        f.write(await file.read())
    with open(wm_path, "wb") as f:
        f.write(await watermark_file.read())

    try:
        # Apel serviciu pentru watermark + metrici + DB
        record = service.create_image(
            filename=file.filename,
            method=method,
            image_path=image_path,
            watermark_path=wm_path,
            format = file.content_type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": "Image uploaded, watermarked and saved successfully",
        "filename": record.filename,
        "method": record.method,
        "psnr": record.psnr,
        "ber": record.ber,
        "width": record.width,
        "height": record.height,
        "format": record.format
    }