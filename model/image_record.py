from sqlalchemy import Column, Integer, String, Float
from dbConnection.database import Base


class ImageRecord(Base):
    __tablename__ = "images"



    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    method = Column(String)  # DCT, DWT, Hibrid
    psnr = Column(Float)
    ber = Column(Float)
    width = Column(Float)
    height = Column(Float)
    format = Column(String)  #.jpg, etc