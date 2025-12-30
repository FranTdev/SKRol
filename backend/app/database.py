import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL", "").strip()
key: str = os.getenv("SUPABASE_KEY", "").strip()

if not url or not key:
    print("WARNING: SUPABASE_URL or SUPABASE_KEY not found in environment")
elif "..." in key:
    print(
        "CRITICAL: You are using a placeholder SUPABASE_KEY. Please replace it with your real key from Supabase."
    )

# Conexión a la nube de Supabase
supabase: Client = (
    create_client(url, key) if (url and key and "..." not in key) else None
)


def get_db():
    return supabase
