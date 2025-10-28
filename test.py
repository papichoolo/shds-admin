import firebase_admin
from firebase_admin import credentials, auth
import requests
import os
from dotenv import load_dotenv
load_dotenv()

cred = credentials.Certificate(r"C:\Users\utfu\Downloads\primeval-gizmo-474808-m7-firebase-adminsdk-fbsvc-60adccb5ba.json")
firebase_admin.initialize_app(cred)

API_KEY = os.getenv("WEB_API_KEY")

custom_token = auth.create_custom_token("test_uid").decode()

r = requests.post(
    f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={API_KEY}",
    json={
        "token": custom_token,
        "returnSecureToken": True
    },
    timeout=10
)

print(r.status_code)
print(r.text)
