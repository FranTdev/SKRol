
-- Add description to campaigns table if not exists
ALTER TABLE public.campaigns 
ADD COLUMN IF NOT EXISTS description TEXT DEFAULT 'Esta es tu campaña en el nivel actual del Haz.';

-- Add manual_url to campaign_rules table if not exists
ALTER TABLE public.campaign_rules 
ADD COLUMN IF NOT EXISTS manual_url TEXT DEFAULT '';
