from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, admin
from app.mcp_server.server import mcp_router
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="MCP-Based Secure AI Database Access Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(admin.router, prefix="/admin")
app.include_router(mcp_router, prefix="/mcp")
