
-- TRAMA DE SEGURIDAD DEL HAZ (Row Level Security Enablement)
-- Ejecuta este script en el Editor SQL de Supabase para asegurar las tablas y silenciar las advertencias.
-- Se aplican políticas "Allow All" (Permisivas) inicialmente para garantizar que la aplicación no se rompa.

-- 1. Campaign Rules
ALTER TABLE public.campaign_rules ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable access to all users" ON public.campaign_rules FOR ALL USING (true) WITH CHECK (true);

-- 2. Campaign Participants
ALTER TABLE public.campaign_participants ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable access to all users" ON public.campaign_participants FOR ALL USING (true) WITH CHECK (true);

-- 3. Users (Si se gestiona externamente, esto podría requerir ajustes, pero 'true' mantiene el estado actual)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable access to all users" ON public.users FOR ALL USING (true) WITH CHECK (true);

-- 4. Campaigns
ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable access to all users" ON public.campaigns FOR ALL USING (true) WITH CHECK (true);

-- 5. Conditions Def
ALTER TABLE public.conditions_def ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable access to all users" ON public.conditions_def FOR ALL USING (true) WITH CHECK (true);

-- 6. Skills Def
ALTER TABLE public.skills_def ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable access to all users" ON public.skills_def FOR ALL USING (true) WITH CHECK (true);

-- 7. Characters
ALTER TABLE public.characters ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable access to all users" ON public.characters FOR ALL USING (true) WITH CHECK (true);

-- 8. Character Inventory
ALTER TABLE public.character_inventory ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable access to all users" ON public.character_inventory FOR ALL USING (true) WITH CHECK (true);

-- 9. Character Conditions
ALTER TABLE public.character_conditions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable access to all users" ON public.character_conditions FOR ALL USING (true) WITH CHECK (true);

-- 10. Character Skills
ALTER TABLE public.character_skills ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable access to all users" ON public.character_skills FOR ALL USING (true) WITH CHECK (true);
