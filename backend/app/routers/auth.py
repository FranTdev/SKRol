from fastapi import APIRouter, HTTPException
from ..database import get_db
from pydantic import BaseModel
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = get_db()


# --- MODELOS (Solo datos de cuenta) ---
class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# --- UTILIDADES ---
def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


# --- RUTAS ---


@router.post("/register")
def register(user: UserRegister):
    # Solo guardamos datos de IDENTIDAD
    user_data = {
        "username": user.username,
        "email": user.email,
        "password_hash": get_password_hash(user.password),
    }

    try:
        response = db.table("users").insert(user_data).execute()
        if response.data:
            return {"message": "Cuenta creada exitosamente", "username": user.username}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al registrar: {str(e)}")


@router.post("/login")
def login(user: UserLogin):
    # Buscamos al usuario
    response = db.table("users").select("*").eq("username", user.username).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user_db = response.data[0]

    # Verificamos password
    if not verify_password(user.password, user_db["password_hash"]):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    # Retornamos solo el ID y Username (La "llave" para luego cargar el juego)
    return {
        "message": "Login correcto",
        "user_id": user_db["id"],
        "username": user_db["username"],
    }
