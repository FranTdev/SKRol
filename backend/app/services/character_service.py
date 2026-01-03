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

        # Optimized: Single select with multi-level joins to fetch all related data in one go
        # Supabase syntax: table(columns), related_table(columns)
        query = (
            db.table("characters")
            .select("""
                *,
                users(username),
                inventory:character_inventory(*),
                skills_rel:character_skills(
                    skills_def(*)
                ),
                conditions:character_conditions(
                    *,
                    conditions_def(*)
                )
            """)
            .eq("campaign_id", campaign_id)
        )

        if not is_admin:
            query = query.eq("user_id", requester_id)

        response = query.execute()
        characters = response.data

        # Post-process to flatten the nested skills structure if needed for frontend backward compatibility
        for char in characters:
            if "skills_rel" in char:
                # character_skills returns a list of objects containing skills_def
                char["skills"] = [
                    s["skills_def"] for s in char["skills_rel"] if s.get("skills_def")
                ]
                del char["skills_rel"]
            else:
                char["skills"] = []

        return characters
    except Exception as e:
        print(f"ERROR in get_campaign_characters_filtered (optimized): {str(e)}")
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
    """
    Syncs the character's 'Estado' in stats and handles active conditions.
    """
    try:
        # Get current stats to update Estado
        char_resp = (
            db.table("characters").select("stats").eq("id", character_id).execute()
        )
        if not char_resp.data:
            raise HTTPException(status_code=404, detail="Personaje no encontrado")

        stats = char_resp.data[0].get("stats") or {}
        stats["Estado"] = status

        # Update character stats
        db.table("characters").update({"stats": stats}).eq("id", character_id).execute()

        return {"id": character_id, "stats": stats, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def hard_delete_character_preserved(character_id: str):
    try:
        # Relational cascades should handle inventory, skills, and conditions
        db.table("characters").delete().eq("id", character_id).execute()
        return {"message": "Personaje eliminado del Haz permanentemente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
