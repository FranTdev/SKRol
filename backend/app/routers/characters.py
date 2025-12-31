from fastapi import APIRouter, HTTPException
from ..database import get_db
from ..models import CharacterCreate
from typing import List, Optional

from ..services import character_service, shining_service

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
def update_character(
    character_id: str, character_data: dict, requester_id: Optional[str] = None
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        # Get current character to check death status and campaign
        char_resp = (
            db.table("characters")
            .select("id, status:stats->>Estado, campaign_id")
            .eq("id", character_id)
            .execute()
        )
        if not char_resp.data:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")

        char_current = char_resp.data[0]
        # We use stats->>Estado or condition->>status as fallback if needed,
        # but the request mentioned stats.Estado refactor.
        is_dead = char_current.get("status") == "muerte"

        if is_dead:
            # Only admin can edit a dead character
            campaign_id = char_current["campaign_id"]
            campaign_resp = (
                db.table("campaigns").select("admin_id").eq("id", campaign_id).execute()
            )
            if (
                not campaign_resp.data
                or campaign_resp.data[0]["admin_id"] != requester_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Solo el Maestro puede interactuar con los caídos en el Haz.",
                )

        # Filter out fields that are not in the database table
        clean_data = {k: v for k, v in character_data.items() if k != "users"}

        response = (
            db.table("characters").update(clean_data).eq("id", character_id).execute()
        )
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{character_id}/condition")
def update_condition(character_id: str, data: dict, requester_id: Optional[str] = None):
    status = data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")

    try:
        # Check if character is already dead and requester is not admin
        char_resp = (
            db.table("characters")
            .select("stats->>Estado, campaign_id")
            .eq("id", character_id)
            .execute()
        )
        if char_resp.data:
            is_dead = char_resp.data[0].get("Estado") == "muerte"
            if is_dead:
                campaign_id = char_resp.data[0]["campaign_id"]
                campaign_resp = (
                    db.table("campaigns")
                    .select("admin_id")
                    .eq("id", campaign_id)
                    .execute()
                )
                if (
                    not campaign_resp.data
                    or campaign_resp.data[0]["admin_id"] != requester_id
                ):
                    raise HTTPException(
                        status_code=403,
                        detail="Solo el Maestro puede alterar el destino de los caídos.",
                    )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error checking death status: {e}")

    return character_service.update_character_condition(character_id, status)


@router.patch("/{character_id}/transfer")
def transfer_owner(character_id: str, data: dict):
    new_owner_id = data.get("new_owner_id")
    if not new_owner_id:
        raise HTTPException(status_code=400, detail="new_owner_id is required")
    return character_service.transfer_character_ownership(character_id, new_owner_id)


@router.post("/{character_id}/shining")
def generate_shining(character_id: str, requester_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        # Get character to check campaign
        char_resp = (
            db.table("characters")
            .select("campaign_id")
            .eq("id", character_id)
            .execute()
        )
        if not char_resp.data:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")

        campaign_id = char_resp.data[0]["campaign_id"]

        # Get campaign settings from campaign_rules table
        camp_resp = (
            db.table("campaign_rules")
            .select("*")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        settings = camp_resp.data[0] if camp_resp.data else {}

        # Generate abilities
        abilities = shining_service.generate_shining_abilities(settings)

        if abilities is None:
            return {"message": "No tienes resplandor", "skills": []}

        # Update character with new skills
        db.table("characters").update({"skills": abilities}).eq(
            "id", character_id
        ).execute()

        return {"message": "Resplandor despertado", "skills": abilities}

    except HTTPException:
        raise
    except Exception as e:
        print(f"CRITICAL ERROR in generate_shining: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error del Haz: {str(e)}")


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
