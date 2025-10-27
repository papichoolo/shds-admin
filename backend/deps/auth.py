from fastapi import Header, HTTPException
from firebase_admin import auth as fb_auth, initialize_app

initialize_app()

def get_user(): #will take firebase jwt token from header and verify later
    """try:
        decoded = fb_auth.verify_id_token(x_firebase_token)
    except Exception:
        raise HTTPException(401, "invalid token")
    # derive roles/branch from custom claims or DB
    return {"uid": decoded["uid"], "roles": decoded.get("roles", ["admin"]), "branchId": decoded.get("branchId", "main_siliguri")}
"""
    return {"uid": "dev", "roles": ["admin"], "branchId": "1"}