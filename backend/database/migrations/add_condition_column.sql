
-- ADD CONDITION COLUMN TO CHARACTERS
-- Run this in Supabase SQL Editor to fix the "Could not find the 'condition' column" error.

ALTER TABLE public.characters 
ADD COLUMN condition JSONB DEFAULT '{}'::jsonb;

-- Optional: Add a comment
COMMENT ON COLUMN public.characters.condition IS 'Stores temporary states like death requests or statuses';
