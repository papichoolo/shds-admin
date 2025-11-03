"""User management service."""

from backend.reps.firestore import fs

def setup_user_profile(uid: str, branch_id: str, roles: list[str]) -> dict:
    """Create or update user profile in Firestore."""
    user_ref = fs().collection("users").document(uid)
    
    user_data = {
        "uid": uid,
        "branchId": branch_id,
        "roles": roles,
    }
    
    user_ref.set(user_data, merge=True)
    return user_data

def get_user_profile(uid: str) -> dict | None:
    """Get user profile from Firestore."""
    user_ref = fs().collection("users").document(uid)
    doc = user_ref.get()
    
    if doc.exists:
        return doc.to_dict()
    return None
