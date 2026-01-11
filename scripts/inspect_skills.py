import sys
import os

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from backend.app.database import get_db


def inspect_columns():
    db = get_db()
    try:
        # Fetch one row to see keys
        resp = db.table("skills_def").select("*").limit(1).execute()
        if resp.data:
            print("Columns in skills_def:", resp.data[0].keys())
        else:
            print("Table empty, cannot inspect columns easily without header metadata.")
            # Try inserting a dummy with all fields we expect and see if it errors

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # sys.path handled at top
    inspect_columns()
