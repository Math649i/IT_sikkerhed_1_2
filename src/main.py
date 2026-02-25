from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from flat_file_db import FlatFileDB

# --- Pydantic modeller ---

class UserCreate(BaseModel):
    """Model til oprettelse af bruger (POST)."""
    person_id: str
    first_name: str
    last_name: str
    address: str
    street_number: str
    password: str
    enabled: bool = True
    email: Optional[str] = None
    phone: Optional[str] = None

class UserUpdate(BaseModel):
    """Model til opdatering af bruger (PUT). Alle felter er valgfrie."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    street_number: Optional[str] = None
    password: Optional[str] = None
    enabled: Optional[bool] = None
    email: Optional[str] = None
    phone: Optional[str] = None

# --- App ---

app = FastAPI(
    title="Flat File DB REST API",
    description="REST API til CRUD-operationer på en flat file database med kryptering og hashing.",
    version="1.0.0",
)

db = FlatFileDB("flat_file_db.json")


# --- Endpoints ---

@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    """Opret en ny bruger (Create)."""
    try:
        db.add_user(user.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"message": f"Bruger '{user.person_id}' oprettet."}


@app.get("/users")
def list_users():
    """Hent en oversigt over alle brugere (List)."""
    users = []
    for user in db.users:
        decrypted = db.get_user(user["person_id"])
        if decrypted:
            decrypted.pop("password", None)
            users.append(decrypted)
    return users


@app.get("/users/{person_id}")
def read_user(person_id: str):
    """Hent en enkelt bruger (Read)."""
    user = db.get_user(person_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"Bruger '{person_id}' ikke fundet.")
    user.pop("password", None)
    return user


@app.put("/users/{person_id}")
def update_user(person_id: str, updates: UserUpdate):
    """Opdater en eksisterende bruger (Update)."""
    update_data = updates.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=422, detail="Ingen felter at opdatere.")
    try:
        updated = db.update_user(person_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    updated.pop("password", None)
    return updated


@app.delete("/users/{person_id}")
def delete_user(person_id: str):
    """Slet en bruger (Delete)."""
    try:
        db.delete_user(person_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f"Bruger '{person_id}' slettet."}
