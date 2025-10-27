from fastapi import FastAPI
from routes.students import r as students_router

app = FastAPI(title="shds-admin")
app.include_router(students_router)
