import sys
import os
from backend.app.database import get_db


def inspect_settings():
    db = get_db()
    try:
        camp = db.table("campaigns").select("id").limit(1).execute()
        if not camp.data:
            print("No campaigns.")
            return
        cid = camp.data[0]["id"]

        rules = db.table("campaign_rules").select("*").eq("campaign_id", cid).execute()
        if rules.data:
            print("Campaign Rules found:")
            print(f"shining_prob: {rules.data[0].get('shining_prob')}")
            print(f"max_power: {rules.data[0].get('max_power')}")
        else:
            print("No rules found for this campaign.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    sys.path.append(os.getcwd())
    inspect_settings()
