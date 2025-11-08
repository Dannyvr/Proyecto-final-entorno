from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import endpoints.zones__controller as zones_controller

###### START THE SERVER ######
# To run the server, use the command: uvicorn main:app --reload

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(zones_controller.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI server!"}