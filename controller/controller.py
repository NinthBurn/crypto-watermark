# controller/image_record_controller.py
import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from starlette.responses import FileResponse

from model.image_record import ImageRecord
from service.image_record_service import ImageRecordService
from repository.image_record_repo import ImageRecordRepository

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
    method: str = Form(...)
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
        if method == "DWT":
            record, watermarked_path = service.create_image(
                filename=file.filename,
                method=method,
                image_path=image_path,
                watermark_path=wm_path,
                format=file.content_type
            )

        elif method == "DCT":
            pass
            # record, watermarked_path = service.create_image_dct(
            #     filename=file.filename,
            #     method=method,
            #     image_path=image_path,
            #     watermark_path=wm_path,
            #     format=file.content_type
            # )
        else:
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
    method: str = Form(...)
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

    try:
        if method == "DWT":
            extracted_wm = service.extract_watermark_dwt(
                original_path=orig_path,
                watermarked_path=wm_path
            )
            extracted_path = os.path.join(
                UPLOAD_DIR,
                "extracted_" + original_image.filename
            )
            service.save_extracted_watermark(extracted_wm, extracted_path)

        elif method == "DCT":
            pass
            # extracted_path = service.extract_watermark_dct(orig_path, wm_path)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported extraction method"
            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Returnează imaginea watermark extras
    return FileResponse(
        extracted_path,
        media_type=original_image.content_type,
        filename=f"extracted_{original_image.filename}"
    )