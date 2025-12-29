import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

# Conexión a la nube de Supabase
supabase: Client = create_client(url, key)


def get_supabase():
    return supabase
