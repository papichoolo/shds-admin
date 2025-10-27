from pydantic import BaseModel, Field
from datetime import datetime

class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    guardianPhone: str = Field(min_length=8, max_length=20)
    branchId: str

class Student(BaseModel):
    id: str
    name: str
    guardianPhone: str
    branchId: str
    createdAt: datetime
