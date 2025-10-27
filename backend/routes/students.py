from fastapi import APIRouter, Depends, HTTPException, status
from models.students import StudentCreate, Student
from services.students import create_student
from deps.auth import get_user

r = APIRouter(prefix="/students", tags=["students"])

@r.post("", response_model=Student, status_code=status.HTTP_201_CREATED)
def create(dto: StudentCreate, user=Depends(get_user)):
    if "admin" not in user["roles"] and "staff" not in user["roles"]:
        raise HTTPException(403, "forbidden")
    if user["branchId"] != dto.branchId:
        raise HTTPException(403, "branch scope")
    return create_student(dto, actor_uid=user["uid"])
