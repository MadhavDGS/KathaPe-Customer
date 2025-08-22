-- This file defines the schema for the Appwrite collections.
-- Each collection is defined by a CREATE TABLE statement.
-- Each attribute is defined by a column definition.
-- The format is intended to be parsed by a script that uses the Appwrite API.

-- Users Collection
CREATE TABLE users (
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    user_type VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL
);

-- Customers Collection
CREATE TABLE customers (
    user_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    created_at DATETIME NOT NULL
);

-- Businesses Collection
CREATE TABLE businesses (
    user_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    access_pin VARCHAR(10) NOT NULL,
    created_at DATETIME NOT NULL
);

-- Customer Credits Collection
CREATE TABLE customer_credits (
    customer_id VARCHAR(255) NOT NULL,
    business_id VARCHAR(255) NOT NULL,
    current_balance DECIMAL(10, 2) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- Transactions Collection
CREATE TABLE transactions (
    customer_id VARCHAR(255) NOT NULL,
    business_id VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    type VARCHAR(20) NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL
);