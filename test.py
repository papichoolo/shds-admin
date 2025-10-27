import firebase_admin
from firebase_admin import credentials, auth
import requests

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

custom_token = auth.create_custom_token("test_uid")
r = requests.post(
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=YOUR_API_KEY",
    json={"token": custom_token.decode(), "returnSecureToken": True}
)
print(r.json()["idToken"])
