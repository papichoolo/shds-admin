from fastapi import APIRouter, Depends, HTTPException, status
from models.students import StudentCreate, Student
from services.students import create_student, list_students as list_students_service
from deps.auth import get_user

r = APIRouter(prefix="/students", tags=["students"])

@r.post("", response_model=Student, status_code=status.HTTP_201_CREATED)
def create(dto: StudentCreate, user=Depends(get_user)):
    if "admin" not in user["roles"] and "staff" not in user["roles"]:
        raise HTTPException(403, "forbidden")
    if user["branchId"] != dto.branchId:
        raise HTTPException(403, "branch scope")
    return create_student(dto, actor_uid=user["uid"])

@r.get("", response_model=list[Student])
def list_students(user=Depends(get_user)):
    """Get all students for the user's branch"""
    if "admin" not in user["roles"] and "staff" not in user["roles"]:
        raise HTTPException(403, "forbidden")
    
    if not user["branchId"]:
        raise HTTPException(400, "User has no branch assigned")
    
    return list_students_service(branch_id=user["branchId"])
