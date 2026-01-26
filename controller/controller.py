# controller/image_record_controller.py
import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from dto.image_record_dto import ImageRecordDto
from repository.image_record_repo import ImageRecordRepository
from service.image_record_service import ImageRecordService
from model.image_record import ImageRecord
from PIL import Image

router = APIRouter()
repository = ImageRecordRepository()
service = ImageRecordService(repository)

UPLOAD_DIR = "uploadedImages"  # director unde se salvează imaginile

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/images/upload/", response_model=dict)
async def upload_image(file: UploadFile = File(...), method: str = Form(...)):
    # Verificăm formatul
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Image must be PNG or JPEG")

    # Salvează fișierul local
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Deschide imaginea cu Pillow pentru dimensiuni
    with Image.open(file_location) as img:
        width, height = img.size
        print("width: ", width, ", height: ", height)
        format = img.format  # PNG sau JPEG

    # Verifică dimensiuni min/max
    if width < 256 or height < 256:
        raise HTTPException(status_code=400, detail="Image too small")
    if width > 1024 or height > 1024:
        raise HTTPException(status_code=400, detail="Image too large")

    # Salvează recordul în baza de date
    record = service.create(
        filename=file.filename,
        method=method,
        psnr=0.0,  # aici poți calcula ulterior după watermarking
        ber=0.0,   # idem
        width=width,
        height=height,
        format=format
    )

    return {"message": "Image uploaded and saved successfully"}
