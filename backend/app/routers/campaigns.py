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


# --- ENDPOINTS ---


@router.put("/{campaign_id}")
def update_campaign(campaign_id: str, campaign_data: dict, requester_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        # Verify requester is admin
        camp_resp = (
            db.table("campaigns").select("admin_id").eq("id", campaign_id).execute()
        )
        if not camp_resp.data or camp_resp.data[0]["admin_id"] != requester_id:
            raise HTTPException(
                status_code=403, detail="Solo el Maestro puede modificar el Mundo."
            )

        response = (
            db.table("campaigns").update(campaign_data).eq("id", campaign_id).execute()
        )
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}/settings")
def get_campaign_settings(campaign_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    try:
        response = (
            db.table("campaign_rules")
            .select("*")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        if response.data:
            return response.data[0]

        # If not found, return defaults
        return {
            "campaign_id": campaign_id,
            "rules": "",
            "shining_prob": 1.0,
            "max_power": 50,
            "default_char_limit": 3,
            "abilities_config": [],
        }
    except Exception as e:
        print(f"ERROR in get_campaign_settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error del Haz: {str(e)}")


@router.put("/{campaign_id}/settings")
def update_campaign_settings(campaign_id: str, settings_data: dict, requester_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        # Verify requester is admin
        camp_resp = (
            db.table("campaigns").select("admin_id").eq("id", campaign_id).execute()
        )
        if not camp_resp.data or camp_resp.data[0]["admin_id"] != requester_id:
            raise HTTPException(
                status_code=403, detail="Solo el Maestro puede modificar las reglas."
            )

        # Upsert logic: attempt update, then insert if not exists
        # In Supabase-py, we can use upsert or handle manually
        response = (
            db.table("campaign_rules")
            .upsert({**settings_data, "campaign_id": campaign_id})
            .execute()
        )

        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Error salvaguardando las reglas")
    except HTTPException:
        raise
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


@router.get("/{campaign_id}/participants/limits")
def get_participants_limits(campaign_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    try:
        return campaign_service.get_participants_with_limits(campaign_id)
    except Exception as e:
        print(f"ERROR in get_participants_limits: {str(e)}")
        # If it's a join error, we might want to return something more useful
        raise HTTPException(
            status_code=500, detail=f"Fallo en la conexión de almas: {str(e)}"
        )


@router.patch("/{campaign_id}/participants/{user_id}/limit")
def update_participant_limit_endpoint(campaign_id: str, user_id: str, limit_data: dict):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    limit = limit_data.get("limit")
    if limit is None:
        raise HTTPException(status_code=400, detail="Limit is required")
    return campaign_service.update_participant_limit(campaign_id, user_id, limit)


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
