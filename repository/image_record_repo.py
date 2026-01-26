from sqlalchemy import String
from sqlalchemy.orm import Session
from dbConnection.database import SessionLocal
from model.image_record import ImageRecord

class ImageRecordRepository:
    def __init__(self):
        pass

    def create(self, filename: str, method: str, psnr: float, ber: float, width: float, height: float, format: String) -> ImageRecord:
        with SessionLocal() as db:
            record = ImageRecord(
                filename=filename,
                method=method,
                psnr=psnr,
                ber=ber,
                width=width,
                height=height,
                format=format
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record

    def get_by_id(self, record_id: int) -> ImageRecord | None:
        with SessionLocal() as db:
            return db.query(ImageRecord).filter(ImageRecord.id == record_id).first()

    def get_all(self) -> list[ImageRecord]:
        with SessionLocal() as db:
            return db.query(ImageRecord).all()

    def delete(self, record_id: int) -> bool:
        with SessionLocal() as db:
            record = db.query(ImageRecord).filter(ImageRecord.id == record_id).first()
            if record:
                db.delete(record)
                db.commit()
                return True
            return False