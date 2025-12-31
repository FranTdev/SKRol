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


# --- MODELOS PARA CAMPAÑAS ---


class CampaignCreate(BaseModel):
    name: str
    admin_id: str


class CampaignRules(BaseModel):
    campaign_id: str
    rules: Optional[str] = ""
    shining_prob: float = 1.0
    max_power: int = 50
    default_char_limit: int = 3
    abilities_config: List[Dict] = []


class Campaign(BaseModel):
    id: str
    name: str
    admin_id: str
    created_at: str


# --- MODELOS PARA PERSONAJES ---


class CharacterCreate(BaseModel):
    name: str
    campaign_id: str
    user_id: str
    description: Optional[str] = None
    stats: Dict = {}
    skills: List[Dict] = []
    inventory: List[Dict] = []
    condition: Dict = {}


class Character(CharacterCreate):
    id: str
    created_at: str
