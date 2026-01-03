import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Add backend directory to path to import app modules if needed,
# but here we just need raw connection to test schema
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Load environment variables
load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

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
