from ..database import get_db
from fastapi import HTTPException

db = get_db()


def get_user_campaigns_orchestrated(user_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        # Get campaigns where user is Admin
        admin_campaigns = (
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
        all_campaign_ids = {c["id"] for c in admin_campaigns}
        for c in participant_campaigns:
            if c["id"] not in all_campaign_ids:
                admin_campaigns.append(c)
                all_campaign_ids.add(c["id"])

        return admin_campaigns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_participant_limit(campaign_id: str, user_id: str, limit: int):
    try:
        response = (
            db.table("campaign_participants")
            .update({"char_limit": limit})
            .eq("campaign_id", campaign_id)
            .eq("user_id", user_id)
            .execute()
        )
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_participants_with_limits(campaign_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    # Priority 1: Usernames + char_limit (Perfect)
    try:
        response = (
            db.table("campaign_participants")
            .select("user_id, char_limit, users!user_id(username)")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        if response.data:
            return response.data
    except Exception as e:
        print(f"DEBUG: Perfect query fail (likely missing char_limit): {str(e)}")

    # Priority 2: Usernames only (Fallback if char_limit column is missing)
    try:
        response = (
            db.table("campaign_participants")
            .select("user_id, users!user_id(username)")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        data = response.data
        for p in data:
            p["char_limit"] = 3  # Default fallback for the column
        return data
    except Exception as e:
        print(f"DEBUG: Username query fail: {str(e)}")

    # Priority 3: Only IDs + char_limit (Fallback if users join fails)
    try:
        response = (
            db.table("campaign_participants")
            .select("user_id, char_limit")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        data = response.data
        for p in data:
            p["users"] = {"username": f"Pistolero ({p['user_id'][:8]})"}
        return data
    except Exception as e:
        print(f"DEBUG: Column-only query fail: {str(e)}")

    # Priority 4: Absolute minimum (Only user_id)
    try:
        response = (
            db.table("campaign_participants")
            .select("user_id")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        data = response.data
        for p in data:
            p["char_limit"] = 3
            p["users"] = {"username": f"Pistolero ({p['user_id'][:8]})"}
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo total en el Haz: {str(e)}")
