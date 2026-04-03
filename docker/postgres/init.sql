-- Initialize database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create index for fuzzy search
CREATE OR REPLACE FUNCTION pg_trgm_similarity(text, text) RETURNS float AS $$
    SELECT similarity($1, $2);
$$ LANGUAGE SQL IMMUTABLE;