from __future__ import annotations

import pathlib
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.routes.collections import r as collections_router
from backend.routes.students import r as students_router
from backend.routes.users import r as users_router
app = FastAPI(title="shds-admin")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(students_router)
app.include_router(users_router)
app.include_router(collections_router)
