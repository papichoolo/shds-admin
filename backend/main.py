from fastapi import FastAPI
from routes.students import r as students_router
from routes.users import r as users_router
from fastapi.middleware.cors import CORSMiddleware
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