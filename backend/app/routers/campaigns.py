from fastapi import APIRouter, HTTPException
from ..database import get_db
from ..models import CampaignCreate
from typing import List

from ..services import campaign_service

router = APIRouter()
db = get_db()


@router.post("/", response_model=dict)
def create_campaign(campaign: CampaignCreate):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        response = (
            db.table("campaigns")
            .insert({"name": campaign.name, "admin_id": campaign.admin_id})
            .execute()
        )

        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Error creating campaign")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=List[dict])
def get_user_campaigns(user_id: str):
    return campaign_service.get_user_campaigns_orchestrated(user_id)


@router.get("/{campaign_id}/participants/limits")
def get_participants_limits(campaign_id: str):
    return campaign_service.get_participants_with_limits(campaign_id)


@router.patch("/{campaign_id}/participants/{user_id}/limit")
def update_limit(campaign_id: str, user_id: str, data: dict):
    limit = data.get("limit")
    if limit is None:
        raise HTTPException(status_code=400, detail="Limit is required")
    return campaign_service.update_participant_limit(campaign_id, user_id, limit)


@router.put("/{campaign_id}")
def update_campaign(campaign_id: str, campaign_data: dict):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        response = (
            db.table("campaigns").update(campaign_data).eq("id", campaign_id).execute()
        )
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        db.table("campaigns").delete().eq("id", campaign_id).execute()
        return {"message": "Campaña eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- PARTICIPANTES ---


@router.post("/{campaign_id}/participants")
def add_participant(campaign_id: str, user_id: str, role: str = "player"):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        response = (
            db.table("campaign_participants")
            .insert({"campaign_id": campaign_id, "user_id": user_id, "role": role})
            .execute()
        )
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}/participants")
def get_participants(campaign_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        # Hacemos join con la tabla users para traer el nombre
        # Nota: La sintaxis de Supabase-py para joins es select("*, table(*)")
        response = (
            db.table("campaign_participants")
            .select("role, user_id, users(username)")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{campaign_id}/participants/{user_id}")
def remove_participant(campaign_id: str, user_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        db.table("campaign_participants").delete().eq("campaign_id", campaign_id).eq(
            "user_id", user_id
        ).execute()
        return {"message": "Participante eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
