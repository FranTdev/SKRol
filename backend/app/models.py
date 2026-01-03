from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


# --- USER MODELS ---


class UserRegister(BaseModel):
    username: str
    password: str
    email: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserInDB(BaseModel):
    id: str
    username: str
    email: str


# --- CAMPAIGN MODELS ---


class CampaignCreate(BaseModel):
    name: str
    admin_id: str


class Campaign(BaseModel):
    id: str
    name: str
    admin_id: Optional[str] = None
    created_at: datetime


class CampaignParticipant(BaseModel):
    campaign_id: str
    user_id: str
    role: str


class CampaignRules(BaseModel):
    campaign_id: str
    rules: Optional[str] = ""
    shining_prob: float = 1.0
    max_power: int = 50
    default_char_limit: int = 3
    abilities_config: Dict = {}
    item_pool: List[Dict] = []
    updated_at: Optional[datetime] = None


# --- DEFINITION MODELS ---


class ConditionDef(BaseModel):
    id: Optional[str] = None
    campaign_id: str
    name: str
    description: Optional[str] = None
    effect: Optional[str] = None
    duration: Optional[str] = None


class SkillDef(BaseModel):
    id: Optional[str] = None
    campaign_id: str
    name: str
    description: Optional[str] = None
    range: Optional[str] = None
    ref_tag: Optional[str] = None
    is_active: bool = False


# --- CHARACTER MODELS ---


class CharacterInventory(BaseModel):
    id: Optional[str] = None
    character_id: str
    item_name: str
    description: Optional[str] = None
    quantity: int = 1
    damage_dice: Optional[str] = None


class CharacterCondition(BaseModel):
    id: Optional[str] = None
    character_id: str
    condition_def_id: str
    current_duration_left: Optional[int] = None


class CharacterSkill(BaseModel):
    character_id: str
    skill_def_id: str


class CharacterCreate(BaseModel):
    name: str
    campaign_id: str
    user_id: Optional[str] = None
    description: Optional[str] = None
    stats: Dict = {}


class Character(CharacterCreate):
    id: str
    created_at: datetime
    inventory: List[CharacterInventory] = []
    skills: List[SkillDef] = []
    conditions: List[ConditionDef] = []
