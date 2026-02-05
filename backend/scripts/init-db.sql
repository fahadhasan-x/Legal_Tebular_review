-- Initial database setup script
-- This runs automatically when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify database
SELECT version();
