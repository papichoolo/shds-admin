from datetime import datetime, timezone

from backend.models.students import Student, StudentCreate
from backend.reps.firestore import fs

def create_student(dto: StudentCreate, actor_uid: str) -> Student:
    now = datetime.now(timezone.utc)
    doc = {
        "name": dto.name,
        "guardianPhone": dto.guardianPhone,
        "branchId": dto.branchId,
        "createdAt": now,
        "createdBy": actor_uid,
    }
    ref = fs().collection("students").document()  # server-generated id
    ref.set(doc)
    return Student(id=ref.id, createdAt=now, **{k: doc[k] for k in ("name","guardianPhone","branchId")})

def list_students(branch_id: str) -> list[Student]:
    """List all students for a given branch."""
    students_ref = fs().collection("students")
    query = students_ref.where("branchId", "==", branch_id)
    docs = query.stream()
    
    students = []
    for doc in docs:
        data = doc.to_dict()
        students.append(Student(
            id=doc.id,
            name=data["name"],
            guardianPhone=data["guardianPhone"],
            branchId=data["branchId"],
            createdAt=data["createdAt"]
        ))
    
    return students
