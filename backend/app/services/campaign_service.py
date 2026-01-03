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
    """
    NOTE: The new schema does not have per-participant char_limit.
    This function is kept for API compatibility but currently does nothing
    as the robust schema moved character limits to global campaign_rules.
    """
    # For now, we just return success to avoid breaking the frontend
    # but we should eventually update the frontend to not call this.
    return {"message": "Individual limit not supported in robust schema"}


def get_participants_with_limits(campaign_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected")

    try:
        # Get global default limit
        rules_resp = (
            db.table("campaign_rules")
            .select("default_char_limit")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        default_limit = 3
        if rules_resp.data:
            default_limit = rules_resp.data[0].get("default_char_limit", 3)

        # Get participants
        response = (
            db.table("campaign_participants")
            .select("user_id, role, users!user_id(username)")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        data = response.data
        for p in data:
            p["char_limit"] = default_limit  # Use global default for everyone
        return data
    except Exception as e:
        print(f"ERROR in get_participants_with_limits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fallo en el Haz: {str(e)}")
