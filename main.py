from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from controller import controller
from dbConnection.database import Base, engine

Base.metadata.create_all(bind=engine)
WatermarkAPI = FastAPI()

WatermarkAPI.include_router(controller.router)

WatermarkAPI.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

WatermarkAPI.mount(
    "/frontend", 
    StaticFiles(directory="frontend", html=True),
    name="frontend"
)