# schema/image_record_schema.py
from pydantic import BaseModel

class ImageRecordDto(BaseModel):
    filename: str
    method: str
    psnr: float
    ber: float
    width: int
    height: int
    format: str