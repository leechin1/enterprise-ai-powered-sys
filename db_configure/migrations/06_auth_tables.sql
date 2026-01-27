-- Authentication Tables Migration
-- Migration: 06_auth_tables.sql
-- Description: Creates users and verification tokens tables for authentication

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- VERIFICATION TOKENS TABLE
CREATE TABLE IF NOT EXISTS verification_tokens (
    token_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    token VARCHAR(100) UNIQUE NOT NULL,
    token_type VARCHAR(50) NOT NULL CHECK (token_type IN ('account_creation', 'password_reset')),
    name VARCHAR(200),
    username VARCHAR(100),
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    created_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_verification_tokens_token ON verification_tokens(token);
CREATE INDEX IF NOT EXISTS idx_verification_tokens_email ON verification_tokens(email);
CREATE INDEX IF NOT EXISTS idx_verification_tokens_expires ON verification_tokens(expires_at);

-- Comments
COMMENT ON TABLE users IS 'User accounts for application authentication';
COMMENT ON TABLE verification_tokens IS 'Tokens for account creation and password reset verification';
COMMENT ON COLUMN verification_tokens.token_type IS 'account_creation: admin invites new user, password_reset: user requests password change';
