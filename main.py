from fastapi import FastAPI

from controller import controller
from dbConnection.database import Base, engine

Base.metadata.create_all(bind=engine)
WatermarkAPI = FastAPI()

WatermarkAPI.include_router(controller.router)