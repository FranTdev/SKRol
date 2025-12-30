from fastapi import APIRouter, HTTPException
from ..database import get_db
from ..models import CharacterCreate
from typing import List

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
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        # Check if requester is admin of the campaign
        campaign_resp = (
            db.table("campaigns").select("admin_id").eq("id", campaign_id).execute()
        )
        if not campaign_resp.data:
            raise HTTPException(status_code=404, detail="Campaña no encontrada")

        is_admin = campaign_resp.data[0]["admin_id"] == requester_id

        query = db.table("characters").select("*").eq("campaign_id", campaign_id)

        if not is_admin:
            # If not admin, only show characters belonging to the requester
            query = query.eq("user_id", requester_id)

        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        response = (
            db.table("characters")
            .update(character_data)
            .eq("id", character_id)
            .execute()
        )
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{character_id}")
def delete_character(character_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        # Get character to find campaign_id
        char_resp = (
            db.table("characters")
            .select("campaign_id")
            .eq("id", character_id)
            .execute()
        )
        if not char_resp.data:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")

        campaign_id = char_resp.data[0]["campaign_id"]

        # Get campaign admin
        campaign_resp = (
            db.table("campaigns").select("admin_id").eq("id", campaign_id).execute()
        )
        if not campaign_resp.data:
            raise HTTPException(status_code=404, detail="Campaña no encontrada")

        admin_id = campaign_resp.data[0]["admin_id"]

        # Transfer ownership to admin
        db.table("characters").update({"user_id": admin_id}).eq(
            "id", character_id
        ).execute()

        return {"message": "Personaje transferido al admin exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
