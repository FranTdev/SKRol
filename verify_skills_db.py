import sys
import os
import uuid
from backend.app.database import get_db


def verify_db_interaction():
    print("Verifying database interactions for Shining System...")
    db = get_db()

    if not db:
        print("db not connected")
        return

    # 1. Get a valid campaign
    try:
        camp = db.table("campaigns").select("id").limit(1).execute()
        if not camp.data:
            print("No campaigns found.")
            return
        campaign_id = camp.data[0]["id"]
    except Exception as e:
        print(f"Error fetching campaign: {e}")
        return

    # 2. Try inserting into skills_def
    skill_name = f"TEST_SKILL_{uuid.uuid4()}"
    print(f"Attempting to insert skill: {skill_name}")

    try:
        resp = (
            db.table("skills_def")
            .insert(
                {
                    "campaign_id": campaign_id,
                    "name": skill_name,
                    "description": "Test description",
                    "ref_tag": "C",
                    "is_active": True,
                }
            )
            .execute()
        )

        if resp.data:
            print("SUCCESS: Inserted into skills_def.")
            skill_id = resp.data[0]["id"]

            # Cleanup
            db.table("skills_def").delete().eq("id", skill_id).execute()
            print("Cleanup successful.")
        else:
            print("FAILURE: Inserted but no data returned. Possible RLS issue.")

    except Exception as e:
        print(f"ERROR inserting into skills_def: {e}")


if __name__ == "__main__":
    sys.path.append(os.getcwd())
    verify_db_interaction()
