from fastapi import APIRouter, HTTPException
from ..database import get_db
from ..models import CharacterCreate
from typing import List

from ..services import character_service

router = APIRouter()
db = get_db()


@router.post("/", response_model=dict)
def create_character(character: CharacterCreate):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        response = db.table("characters").insert(character.dict()).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Error creating character")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/{campaign_id}/{requester_id}", response_model=List[dict])
def get_campaign_characters(campaign_id: str, requester_id: str):
    return character_service.get_campaign_characters_filtered(campaign_id, requester_id)


@router.get("/user/{user_id}", response_model=List[dict])
def get_user_characters(user_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        response = db.table("characters").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{character_id}")
def update_character(character_id: str, character_data: dict):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        # Filter out fields that are not in the database table (like joined data 'users')
        # This is a safety measure if the frontend sends extra fields
        clean_data = {k: v for k, v in character_data.items() if k != "users"}

        response = (
            db.table("characters").update(clean_data).eq("id", character_id).execute()
        )
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{character_id}/condition")
def update_condition(character_id: str, data: dict):
    status = data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")
    return character_service.update_character_condition(character_id, status)


@router.patch("/{character_id}/transfer")
def transfer_owner(character_id: str, data: dict):
    new_owner_id = data.get("new_owner_id")
    if not new_owner_id:
        raise HTTPException(status_code=400, detail="new_owner_id is required")
    return character_service.transfer_character_ownership(character_id, new_owner_id)


@router.delete("/{character_id}")
def delete_character(character_id: str):
    # This remains as the "ownership transfer to admin" logic for the frontend delete button
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        char_resp = (
            db.table("characters")
            .select("campaign_id")
            .eq("id", character_id)
            .execute()
        )
        if not char_resp.data:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")

        campaign_id = char_resp.data[0]["campaign_id"]
        campaign_resp = (
            db.table("campaigns").select("admin_id").eq("id", campaign_id).execute()
        )
        if not campaign_resp.data:
            raise HTTPException(status_code=404, detail="Campaña no encontrada")

        admin_id = campaign_resp.data[0]["admin_id"]
        return character_service.transfer_character_ownership(character_id, admin_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{character_id}/permanent")
def delete_character_permanent(character_id: str):
    # This is for the admin to fully remove a character
    return character_service.hard_delete_character_preserved(character_id)
