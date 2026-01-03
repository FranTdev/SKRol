-- 1. TABLA DE CAMPAÑAS
CREATE TABLE campaigns (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    admin_id UUID REFERENCES users(id) NOT NULL, -- El Game Master
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 2. TABLA DE PARTICIPANTES (Quién juega en qué campaña)
CREATE TABLE campaign_participants (
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'player', -- 'master' o 'player'
    char_limit INTEGER DEFAULT 3, -- Límite de personajes vivos
    PRIMARY KEY (campaign_id, user_id)
);

-- 3. TABLA DE PERSONAJES
CREATE TABLE characters (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- Dueño del personaje
    
    name TEXT NOT NULL,
    description TEXT,
    
    -- AQUÍ GUARDAMOS TUS ESTRUCTURAS COMPLEJAS COMO JSON
    -- Esto permite guardar listas, objetos anidados y lógica flexible
    stats JSONB DEFAULT '{}'::jsonb,        -- Vitalidad, Fuerza, Resplandor, etc.
    skills JSONB DEFAULT '[]'::jsonb,       -- Lista de Habilidades (con sus efectos colaterales)
    inventory JSONB DEFAULT '[]'::jsonb,    -- Lista de Items
    condition JSONB DEFAULT '{}'::jsonb,    -- Condición actual (Muerto, Envenenado, etc.)
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 4. TABLA DE REGLAS Y CONFIGURACIÓN DE CAMPAÑA
CREATE TABLE campaign_rules (
    campaign_id UUID PRIMARY KEY REFERENCES campaigns(id) ON DELETE CASCADE,
    rules TEXT,
    shining_prob FLOAT DEFAULT 1.0,
    max_power INTEGER DEFAULT 50,
    default_char_limit INTEGER DEFAULT 3,
    abilities_config JSONB DEFAULT '[]'::jsonb,
    item_pool JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Desactivar seguridad por ahora para desarrollar rápido
ALTER TABLE campaigns DISABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_participants DISABLE ROW LEVEL SECURITY;
ALTER TABLE characters DISABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_rules DISABLE ROW LEVEL SECURITY;
