from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router

app = FastAPI(title="MedSync API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "ok", "mensagem": "MedSync API online"}
