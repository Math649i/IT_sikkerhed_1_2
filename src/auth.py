from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from flat_file_db import FlatFileDB
import os
from dotenv import load_dotenv

# --- Environment / Secrets ---
# Load test secrets fra .env.test (ligger i git)
# I produktion: sæt rigtige env vars i stedet
if os.path.exists(".env.test"):
    load_dotenv(".env.test")

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# --- Database ---
db = FlatFileDB("user_db.json")

def _ensure_admin():
    """Opret default admin-bruger hvis databasen er tom."""
    if not db.users:
        admin_data = {
            "person_id": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "address": "System",
            "street_number": "0",
            "password": DEFAULT_ADMIN_PASSWORD,
            "enabled": True,
            "role": "admin",
        }
        db.add_user(admin_data)

_ensure_admin()

# --- Pydantic modeller ---

class RegisterRequest(BaseModel):
    person_id: str
    first_name: str
    last_name: str
    address: str
    street_number: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- App ---

app = FastAPI(
    title="Auth REST API",
    description="Authorization REST API med JWT security tokens (Opgave 2).",
    version="1.0.0",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- Hjælpefunktioner ---

def _create_token(person_id: str, role: str) -> str:
    """Opret JWT token med udløbstid."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {"sub": person_id, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def _verify_password(person_id: str, password: str) -> bool:
    """Tjek om password matcher den hashede version i databasen."""
    user = db.get_user(person_id)
    if not user:
        return False
    expected_hash = db._hash_password(password)
    # get_user returnerer den hashede password
    return user["password"] == expected_hash

def _get_current_user(token: str = Depends(oauth2_scheme)):
    """Dekod JWT token og returner brugerdata."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        person_id = payload.get("sub")
        if person_id is None:
            raise HTTPException(status_code=401, detail="Ugyldig token.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Ugyldig eller udløbet token.")

    user = db.get_user(person_id)
    if not user:
        raise HTTPException(status_code=401, detail="Bruger ikke fundet.")
    if not user.get("enabled", True):
        raise HTTPException(status_code=403, detail="Account er deaktiveret.")
    return user

# --- Endpoints ---

@app.post("/auth/token", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login og få en JWT security token."""
    if not _verify_password(form_data.username, form_data.password):
        raise HTTPException(status_code=401, detail="Forkert brugernavn eller password.")

    user = db.get_user(form_data.username)
    if not user.get("enabled", True):
        raise HTTPException(status_code=403, detail="Account er deaktiveret.")

    role = user.get("role", "user")
    token = _create_token(form_data.username, role)
    return TokenResponse(access_token=token)


@app.post("/auth/register", status_code=201)
def register(req: RegisterRequest):
    """Registrer en ny account."""
    user_data = req.model_dump(exclude_none=True)
    user_data["enabled"] = True
    user_data["role"] = "user"
    try:
        db.add_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"message": f"Account '{req.person_id}' oprettet."}


@app.put("/auth/change-password")
def change_password(req: ChangePasswordRequest, current_user: dict = Depends(_get_current_user)):
    """Skift password på den aktuelle bruger (kræver token)."""
    if not _verify_password(current_user["person_id"], req.old_password):
        raise HTTPException(status_code=400, detail="Gammelt password er forkert.")

    db.update_user(current_user["person_id"], {"password": req.new_password})
    return {"message": "Password ændret."}


@app.put("/auth/deactivate")
def deactivate_self(current_user: dict = Depends(_get_current_user)):
    """Deaktiver din egen account (kræver token)."""
    db.update_user(current_user["person_id"], {"enabled": False})
    return {"message": f"Account '{current_user['person_id']}' deaktiveret."}


@app.put("/auth/reactivate/{person_id}")
def reactivate_user(person_id: str, current_user: dict = Depends(_get_current_user)):
    """Reaktiver en account (kun admin)."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Kun admin kan reaktivere accounts.")

    target = db.get_user(person_id)
    if not target:
        raise HTTPException(status_code=404, detail=f"Bruger '{person_id}' ikke fundet.")

    db.update_user(person_id, {"enabled": True})
    return {"message": f"Account '{person_id}' reaktiveret."}


@app.get("/auth/me")
def get_me(current_user: dict = Depends(_get_current_user)):
    """Se din egen profil (kræver token)."""
    current_user.pop("password", None)
    return current_user
