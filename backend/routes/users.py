from fastapi import APIRouter, Depends, HTTPException
from deps.auth import get_user
from services.users import setup_user_profile, get_user_profile
from pydantic import BaseModel

r = APIRouter(prefix="/users", tags=["users"])

class UserSetup(BaseModel):
    branchId: str
    roles: list[str]

@r.post("/setup")
def setup_user(setup: UserSetup, user=Depends(get_user)):
    """Setup user with branch and roles"""
    try:
        user_data = setup_user_profile(
            uid=user["uid"],
            branch_id=setup.branchId,
            roles=setup.roles
        )
        return {
            **user_data,
            "message": "User setup complete"
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to setup user: {str(e)}")

@r.get("/me")
def get_current_user(user=Depends(get_user)):
    """Get current user info"""
    return user