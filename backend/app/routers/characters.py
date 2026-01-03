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
        # Filter only fields that are in the actual table
        char_payload = {
            "name": character.name,
            "campaign_id": character.campaign_id,
            "user_id": character.user_id,
            "description": character.description,
            "stats": character.stats,
        }

        response = db.table("characters").insert(char_payload).execute()
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
        # 1. Get current character to check state and campaign
        char_curr_resp = (
            db.table("characters")
            .select("id, stats, campaign_id")
            .eq("id", character_id)
            .execute()
        )
        if not char_curr_resp.data:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")

        char_current = char_curr_resp.data[0]
        # Check "Estado" in stats
        is_dead = (
            char_current.get("stats", {}).get("Estado") or ""
        ).lower() == "muerte"

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

        # 2. Update character table
        valid_fields = ["name", "description", "stats", "user_id"]
        clean_data = {k: v for k, v in character_data.items() if k in valid_fields}

        # If data is same, update might return empty or same row
        db.table("characters").update(clean_data).eq("id", character_id).execute()

        # 3. Handle Relational Updates (Inventory)
        if "inventory" in character_data:
            # Bulk operation: Delete then Batch Insert
            db.table("character_inventory").delete().eq(
                "character_id", character_id
            ).execute()

            inv_items = character_data["inventory"]
            if inv_items:
                prepared_items = [
                    {
                        "character_id": character_id,
                        "item_name": item.get("item_name") or item.get("name"),
                        "description": item.get("description") or item.get("desc"),
                        "quantity": item.get("quantity", 1),
                        "damage_dice": item.get("damage_dice") or item.get("formula"),
                    }
                    for item in inv_items
                ]
                db.table("character_inventory").insert(prepared_items).execute()

        # 4. Handle Relational Updates (Skills sync - if provided)
        if "skills" in character_data:
            # Logic for manual skill sync could be added here if needed
            pass

        # 5. Return the full character with relations using the service fetch
        refetched = character_service.get_campaign_characters_filtered(
            char_current["campaign_id"], requester_id
        )
        for rc in refetched:
            if rc["id"] == character_id:
                return rc

        return char_current  # Fallback
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in update_character: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{character_id}/condition")
def update_condition(character_id: str, data: dict, requester_id: Optional[str] = None):
    status = data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")

    try:
        char_resp = (
            db.table("characters")
            .select("stats, campaign_id")
            .eq("id", character_id)
            .execute()
        )
        if char_resp.data:
            estado = (char_resp.data[0].get("stats", {}).get("Estado") or "").lower()
            if estado == "muerte":
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
        char_resp = (
            db.table("characters")
            .select("campaign_id")
            .eq("id", character_id)
            .execute()
        )
        if not char_resp.data:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")

        campaign_id = char_resp.data[0]["campaign_id"]

        camp_resp = (
            db.table("campaign_rules")
            .select("*")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        settings = camp_resp.data[0] if camp_resp.data else {}

        abilities = shining_service.generate_shining_abilities(settings)

        if abilities is None:
            return {"message": "No tienes resplandor", "skills": []}

        # Clear old associations
        db.table("character_skills").delete().eq("character_id", character_id).execute()

        character_skills_links = []
        for skill in abilities:
            skill_name = skill["tag"]
            skill_desc = skill["effect"]
            skill_rank = skill["rank"]

            # Find or Create skill definition
            def_resp = (
                db.table("skills_def")
                .select("id")
                .eq("campaign_id", campaign_id)
                .eq("name", skill_name)
                .execute()
            )

            if def_resp.data:
                skill_def_id = def_resp.data[0]["id"]
            else:
                new_def = (
                    db.table("skills_def")
                    .insert(
                        {
                            "campaign_id": campaign_id,
                            "name": skill_name,
                            "description": skill_desc,
                            "ref_tag": skill_rank,
                            "is_active": True,
                        }
                    )
                    .execute()
                )
                skill_def_id = new_def.data[0]["id"]

            character_skills_links.append(
                {"character_id": character_id, "skill_def_id": skill_def_id}
            )

        # Bulk Associate
        if character_skills_links:
            db.table("character_skills").insert(character_skills_links).execute()

        return {"message": "Resplandor despertado", "skills": abilities}

    except HTTPException:
        raise
    except Exception as e:
        print(f"CRITICAL ERROR in generate_shining: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error del Haz: {str(e)}")


@router.delete("/{character_id}")
def delete_character(character_id: str):
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
    return character_service.hard_delete_character_preserved(character_id)
