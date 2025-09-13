-- Simple Website Monitor Database Schema
-- Only user and monitor tables

-- ==========================================
-- Users Table
-- ==========================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    passhash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    verification_otp VARCHAR(10),
    otp_expiry TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- Monitors Table 
-- ==========================================
CREATE TABLE monitors (
    monitorid SERIAL PRIMARY KEY,
    userid INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sitename VARCHAR(255) NOT NULL,
    site_url VARCHAR(500) NOT NULL,
    monitor_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_checked TIMESTAMP,
    status VARCHAR(20) DEFAULT 'unknown' -- up, down, unknown
);

-- ==========================================
-- Indexes for better performance
-- ==========================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_monitors_userid ON monitors(userid);
CREATE INDEX idx_monitors_status ON monitors(status);