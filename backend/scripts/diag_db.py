import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("Missing credentials")
    exit(1)

supabase = create_client(url, key)

print("--- DIAGNOSTIC START ---")
campaign_id = "INSERT_CAMPAIGN_ID_HERE"  # Need to get this from user or search

# Try to get one campaign to use its ID
try:
    c_resp = supabase.table("campaigns").select("id").limit(1).execute()
    if c_resp.data:
        campaign_id = c_resp.data[0]["id"]
        print(f"Using test campaign_id: {campaign_id}")
    else:
        print("No campaigns found to test.")
        exit(0)
except Exception as e:
    print(f"Error fetching campaign: {e}")
    exit(1)

# Test 1: Simple select on participants
print("\nTest 1: Simple select (user_id)")
try:
    resp = (
        supabase.table("campaign_participants")
        .select("user_id")
        .eq("campaign_id", campaign_id)
        .execute()
    )
    print("SUCCESS: Found participants")
    print(resp.data[:2])
except Exception as e:
    print(f"FAIL: {e}")

# Test 2: Select with char_limit
print("\nTest 2: Select with char_limit")
try:
    resp = (
        supabase.table("campaign_participants")
        .select("user_id, char_limit")
        .eq("campaign_id", campaign_id)
        .execute()
    )
    print("SUCCESS: Found char_limit")
except Exception as e:
    print(f"FAIL: {e}")

# Test 3: Join with users
print("\nTest 3: Join with users(username)")
try:
    resp = (
        supabase.table("campaign_participants")
        .select("user_id, users(username)")
        .eq("campaign_id", campaign_id)
        .execute()
    )
    print("SUCCESS: Join users worked")
except Exception as e:
    print(f"FAIL: {e}")

# Test 4: Join with explicit FK
print("\nTest 4: Join with users!user_id(username)")
try:
    resp = (
        supabase.table("campaign_participants")
        .select("user_id, users!user_id(username)")
        .eq("campaign_id", campaign_id)
        .execute()
    )
    print("SUCCESS: Explicit join worked")
except Exception as e:
    print(f"FAIL: {e}")

print("\n--- DIAGNOSTIC END ---")
