-- Run this in the Supabase SQL Editor (Dashboard > SQL Editor > New Query)
-- Creates a content store table for LinkedIn Content Ops
-- No FK to auth.users — this is a single-user tool using service key

CREATE TABLE IF NOT EXISTS linkedin_content_store (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    data JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_linkedin_content_key ON linkedin_content_store (key);

-- No RLS — this table is accessed only via service key
-- The app uses password auth, not Supabase Auth
ALTER TABLE linkedin_content_store DISABLE ROW LEVEL SECURITY;
