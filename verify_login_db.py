import sys
import os
from backend.app.database import get_db


def test_user_access():
    print("Testing access to 'users' table...")
    db = get_db()
    if not db:
        print("CRITICAL: Database client is None. Check env vars.")
        return

    try:
        # Try to select all users
        print("Attempting: db.table('users').select('*').limit(1).execute()")
        response = db.table("users").select("*").limit(1).execute()

        print("Response received.")
        if response.data is not None:
            print(f"SUCCESS. Found {len(response.data)} users (limit 1).")
        else:
            print("SUCCESS? Data is None (might be empty table).")

    except Exception as e:
        print(f"FAILURE: {e}")
        print(
            "Analysis: If this is a 'policy violates row security' error, then RLS is enabled but policies are missing."
        )


if __name__ == "__main__":
    sys.path.append(os.getcwd())
    test_user_access()
