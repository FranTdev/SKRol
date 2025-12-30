from fastapi import APIRouter, HTTPException
from ..database import get_db
from ..models import CampaignCreate
from typing import List

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
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        # Get campaigns where user is Admin, including admin's username
        admin_campaigns_resp = (
            db.table("campaigns")
            .select("*, admin:users!admin_id(username)")
            .eq("admin_id", user_id)
            .execute()
        ).data

        # Get campaigns where user is Participant
        participant_resp = (
            db.table("campaign_participants")
            .select("campaign_id, campaigns(*, admin:users!admin_id(username))")
            .eq("user_id", user_id)
            .execute()
        ).data

        participant_campaigns = [
            p["campaigns"] for p in participant_resp if p.get("campaigns")
        ]

        # Combine and remove duplicates
        all_campaign_ids = {c["id"] for c in admin_campaigns_resp}
        for c in participant_campaigns:
            if c["id"] not in all_campaign_ids:
                admin_campaigns_resp.append(c)
                all_campaign_ids.add(c["id"])

        return admin_campaigns_resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
