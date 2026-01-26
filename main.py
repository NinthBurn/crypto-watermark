from fastapi import FastAPI

from dbConnection.database import Base, engine

Base.metadata.create_all(bind=engine)
WatermarkAPI = FastAPI()

@WatermarkAPI.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}