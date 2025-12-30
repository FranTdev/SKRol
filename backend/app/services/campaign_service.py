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
    try:
        response = (
            db.table("campaign_participants")
            .select("user_id, char_limit, users(username)")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
