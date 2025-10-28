# SHDS Admin Frontend

A Firebase Authentication-based login system for the SHDS Admin application.

## Features

- **Email/Password Authentication**: Sign in with email and password
- **Google Sign-In**: Quick authentication using Google accounts
- **Password Reset**: Forgot password functionality
- **Token Management**: Automatic Firebase ID token handling
- **Responsive Design**: Mobile-friendly interface
- **Dashboard**: Protected dashboard with API integration examples

## Files

- `login.html` - Login page with Firebase authentication
- `dashboard.html` - Protected dashboard page (requires authentication)

## Setup Instructions

### 1. Firebase Configuration

The Firebase configuration is already included in the HTML files:

```javascript
const firebaseConfig = {
    apiKey: "AIzaSyC-9juHGlihMTL10one9WKb8t_QRzEMPpk",
    authDomain: "primeval-gizmo-474808-m7.firebaseapp.com",
    projectId: "primeval-gizmo-474808-m7",
    storageBucket: "primeval-gizmo-474808-m7.firebasestorage.app",
    messagingSenderId: "720912597513",
    appId: "1:720912597513:web:49846f810668037e692ed8"
};
```

### 2. Enable Authentication Methods in Firebase Console

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `primeval-gizmo-474808-m7`
3. Navigate to **Authentication** → **Sign-in method**
4. Enable the following providers:
   - **Email/Password**: Enable this provider
   - **Google**: Enable and configure OAuth consent screen

### 3. Create Test User (Optional)

In Firebase Console → Authentication → Users:
- Click "Add user"
- Enter email and password
- This user can then log in through the frontend

### 4. Run the Frontend

You can run the frontend in several ways:

#### Option A: Simple HTTP Server (Python)

```powershell
cd frontend
python -m http.server 8080
```

Then open: http://localhost:8080/login.html

#### Option B: Live Server (VS Code Extension)

1. Install the "Live Server" extension in VS Code
2. Right-click on `login.html`
3. Select "Open with Live Server"

#### Option C: Direct File Access

Simply open `login.html` in your browser. However, some features may be limited due to CORS restrictions.

### 5. Configure Backend CORS

Update your backend to allow requests from the frontend. In your FastAPI app, add:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5500"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6. Update API Base URL

In `dashboard.html`, update the API base URL to match your backend:

```javascript
const API_BASE_URL = 'http://localhost:8000'; // Change to your backend URL
```

## Usage

### Login Flow

1. Open `login.html` in your browser
2. Sign in using one of these methods:
   - Enter email and password, click "Sign In"
   - Click "Continue with Google"
3. After successful authentication:
   - User info is displayed
   - Firebase ID token is generated and stored
   - Optionally, redirect to dashboard

### Making Authenticated API Calls

The Firebase ID token is sent in the `x-firebase-token` header:

```javascript
const response = await fetch('http://localhost:8000/students', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
        'x-firebase-token': currentToken  // Firebase ID token
    }
});
```

### Backend Integration

Your backend's `auth.py` already handles token verification:

```python
def get_user(x_firebase_token: str | None = Header(default=None)):
    """Validate a Firebase ID token and return the caller context."""
    if not x_firebase_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing firebase token",
        )
    
    decoded = fb_auth.verify_id_token(x_firebase_token)
    return {
        "uid": decoded["uid"],
        "roles": decoded.get("roles", []),
        "branchId": decoded.get("branchId"),
    }
```

## Token Storage

- Firebase ID tokens are stored in `localStorage` with key `firebase_token`
- Tokens automatically refresh when needed
- Tokens are removed on logout

## Security Considerations

1. **HTTPS**: Use HTTPS in production (Firebase requires it for some features)
2. **Token Expiration**: Firebase ID tokens expire after 1 hour and refresh automatically
3. **Secure Storage**: Consider using more secure storage than localStorage for sensitive data
4. **CORS**: Configure CORS properly to only allow trusted origins
5. **API Keys**: The Firebase API key in the config is safe to expose (it's not a secret)

## Customization

### Styling

The login page includes inline CSS that you can customize:
- Colors
- Fonts
- Layout
- Button styles

### Redirect After Login

Uncomment this code in `login.html` to redirect after login:

```javascript
// Optional: Redirect to dashboard after a delay
setTimeout(() => {
    window.location.href = '/dashboard.html';
}, 2000);
```

### Additional Firebase Features

You can add more Firebase features:
- Email verification
- Phone authentication
- Anonymous authentication
- Multi-factor authentication

## Troubleshooting

### "Missing or insufficient permissions" error

- Check that your Firebase user has been created
- Verify Firebase Auth is enabled in console

### CORS errors

- Ensure your backend has CORS configured
- Check that the frontend URL is in the allowed origins

### "Invalid API key" error

- Verify the Firebase config matches your project
- Check Firebase project settings

### Token not being sent

- Check browser console for errors
- Verify token is stored in localStorage
- Ensure user is authenticated before making API calls

## Development vs Production

### Development Mode

The backend has a `DEV_AUTH_BYPASS` environment variable that bypasses authentication:

```python
if os.getenv("DEV_AUTH_BYPASS"):
    return _dev_user()
```

### Production Mode

In production:
- Remove or set `DEV_AUTH_BYPASS=false`
- Use HTTPS for all connections
- Configure proper CORS origins
- Set up proper Firebase security rules

## Next Steps

1. Set up proper routing (consider using a framework like React, Vue, or Angular)
2. Add more pages (student management, reports, etc.)
3. Implement role-based access control
4. Add loading states and better error handling
5. Set up proper build process for production
6. Add analytics and monitoring
