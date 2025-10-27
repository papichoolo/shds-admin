from datetime import datetime, timezone
from models.students import StudentCreate, Student
from reps.firestore import fs

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
