from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import endpoints.zones__controller as zones_controller
import endpoints.threats__controller as threats_controller

###### START THE SERVER ######
# To run the server, use the command: uvicorn main:app --reload

app = FastAPI()


# Manejador global para convertir 422 a 400
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convierte errores 422 de validación a 400"""
    return JSONResponse(
        status_code=400,
        content={"error": "Datos inválidos o faltantes"}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(zones_controller.router)
app.include_router(threats_controller.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI server!"}