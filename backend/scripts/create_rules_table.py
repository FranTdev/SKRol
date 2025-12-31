import os
from supabase import create_client, Client
from dotenv import load_dotenv


def create_table():
    load_dotenv()
    url: str = os.getenv("SUPABASE_URL", "").strip()
    key: str = os.getenv("SUPABASE_KEY", "").strip()

    if not url or not key:
        print("Error: SUPABASE_URL or SUPABASE_KEY not found")
        return

    supabase: Client = create_client(url, key)

    # Supabase-py doesn't have a direct 'execute_sql' method in the client
    # but we can try to use a RPC if they have one set up, or just tell the user.
    # Most developers use the SQL Editor in Supabase UI.

    sql = """
    CREATE TABLE IF NOT EXISTS campaign_rules (
        campaign_id UUID PRIMARY KEY REFERENCES campaigns(id) ON DELETE CASCADE,
        rules TEXT,
        shining_prob FLOAT DEFAULT 1.0,
        max_power INTEGER DEFAULT 50,
        abilities_config JSONB DEFAULT '[]'::jsonb,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    ALTER TABLE campaign_rules DISABLE ROW LEVEL SECURITY;
    """

    print("--- SQL TO RUN IN SUPABASE SQL EDITOR ---")
    print(sql)
    print("------------------------------------------")
    print(
        "Por favor, copia y pega el SQL anterior en el SQL Editor de tu Dashboard de Supabase."
    )


if __name__ == "__main__":
    create_table()
