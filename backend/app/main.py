from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.query import router as query_router

from app.api.health import router as health_router
from app.api.upload import router as upload_router

app = FastAPI(
    title="CodeCompass AI",
    description="Conversational AI for understanding software repositories.",
    version="1.0.0"
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(upload_router)
app.include_router(query_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to CodeCompass AI"
    }
