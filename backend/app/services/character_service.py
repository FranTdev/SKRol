from ..database import get_db
from fastapi import HTTPException

db = get_db()


def get_campaign_characters_filtered(campaign_id: str, requester_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        # Check if requester is admin
        campaign_resp = (
            db.table("campaigns").select("admin_id").eq("id", campaign_id).execute()
        )
        if not campaign_resp.data:
            raise HTTPException(status_code=404, detail="Campaña no encontrada")

        is_admin = campaign_resp.data[0]["admin_id"] == requester_id

        # Select everything plus join with users for the owner username
        query = (
            db.table("characters")
            .select("*, users(username)")
            .eq("campaign_id", campaign_id)
        )

        if not is_admin:
            query = query.eq("user_id", requester_id)

        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def transfer_character_ownership(character_id: str, new_owner_id: str):
    try:
        response = (
            db.table("characters")
            .update({"user_id": new_owner_id})
            .eq("id", character_id)
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_character_condition(character_id: str, status: str):
    try:
        # Get current condition to merge or replace
        char_resp = (
            db.table("characters").select("condition").eq("id", character_id).execute()
        )
        if not char_resp.data:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")

        condition = char_resp.data[0].get("condition") or {}
        condition["status"] = status

        # Sync with stats.Estado refactor
        updates = {"condition": condition}
        char_data = char_resp.data[0]
        stats = char_data.get("stats") or {}
        stats["Estado"] = status
        updates["stats"] = stats

        response = (
            db.table("characters").update(updates).eq("id", character_id).execute()
        )
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def hard_delete_character_preserved(character_id: str):
    """
    PRESERVED: Original hard delete logic. Not used by default as per requirements.
    """
    try:
        db.table("characters").delete().eq("id", character_id).execute()
        return {"message": "Personaje eliminado del Haz permanentemente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
