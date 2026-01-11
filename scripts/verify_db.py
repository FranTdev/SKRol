import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Robust path setup for .env
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# Path to backend .env
env_path = os.path.join(parent_dir, "backend", ".env")
load_dotenv(env_path)

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in backend/.env")
    sys.exit(1)

supabase: Client = create_client(url, key)

try:
    print("Attempting to select stats_order from characters table...")
    # calculating if stats_order exists by selecting it from one record
    response = supabase.table("characters").select("stats_order").limit(1).execute()
    print("Success! Response:", response)
    # If we get here, the column likely exists (or at least no error was thrown)
    # Check if data has the key
    if response.data and isinstance(response.data, list):
        if "stats_order" in response.data[0]:
            print("Column 'stats_order' exists and was retrieved.")
        else:
            print(
                "Response data missing 'stats_order' key. It might be ignored if column doesn't exist but no error thrown?"
            )
    else:
        print("No data returned, but query executed successfully.")

except Exception as e:
    print(f"Error: {e}")
    print("Likely the column 'stats_order' does not exist.")
