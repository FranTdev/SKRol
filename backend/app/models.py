from pydantic import BaseModel
from typing import Optional, List, Dict

# Modelo para registrarse
class UserRegister(BaseModel):
    username: str
    password: str
    email: str

# Modelo para login
class UserLogin(BaseModel):
    username: str
    password: str

# Modelo de cómo se ve un usuario guardado (sin password plano)
class UserInDB(BaseModel):
    id: str
    username: str
    email: str
    level: int
    inventory: List[Dict] = [] # Lista de objetos