from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from scheduled_tasks.resources_check_task import resources_completion_task
from apscheduler.schedulers.background import BackgroundScheduler
import endpoints.zones__controller as zones_controller
import endpoints.threats__controller as threats_controller
import endpoints.resources__controller as resources_controller
from services.threat_scheduler import threat_scheduler
from config.scheduler_config import SchedulerConfig
from services.resource_scheduler import resource_scheduler
from config.resources_scheduler_config import ResourcesSchedulerConfig

###### START THE SERVER ######
# To run the server, use the command: uvicorn main:app --reload

app = FastAPI()

scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    print("Starting scheduler...")
    scheduler.add_job(resources_completion_task, "interval", minutes=2)
    scheduler.start()
    print("Scheduler started")

@app.on_event("shutdown")
def stop_scheduler():
    print("Stopping scheduler...")
    scheduler.shutdown()
    print("Scheduler stopped")

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
app.include_router(resources_controller.router)
app.include_router(threats_controller.router)


@app.on_event("startup")
async def startup_event():
    """Evento de inicio: inicia el scheduler de amenazas automáticas"""
    if SchedulerConfig.AUTO_START:
        threat_scheduler.start()
    if ResourcesSchedulerConfig.AUTO_START:
        resource_scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre: detiene el scheduler de amenazas automáticas"""
    threat_scheduler.stop()
    resource_scheduler.stop()


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI server!"}