-- KhataPe Customer Application Database Setup
-- This file contains all necessary SQL commands to create the required tables
-- Execute these commands in your PostgreSQL database to set up the schema

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (use with caution!)
-- Uncomment the lines below if you want to recreate tables
-- DROP TABLE IF EXISTS customer_credits CASCADE;
-- DROP TABLE IF EXISTS transactions CASCADE;
-- DROP TABLE IF EXISTS customers CASCADE;
-- DROP TABLE IF EXISTS businesses CASCADE;

-- =====================================================
-- CUSTOMERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create index on phone for faster lookups
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);

-- =====================================================
-- BUSINESSES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS businesses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    access_pin VARCHAR(10) UNIQUE NOT NULL,
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_businesses_phone ON businesses(phone);
CREATE INDEX IF NOT EXISTS idx_businesses_access_pin ON businesses(access_pin);

-- =====================================================
-- TRANSACTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL DEFAULT 'payment',
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_business_id ON transactions(business_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);

-- =====================================================
-- CUSTOMER_CREDITS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS customer_credits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, business_id)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_customer_credits_customer_id ON customer_credits(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_credits_business_id ON customer_credits(business_id);

-- =====================================================
-- PENDING_PAYMENTS TABLE (Optional - for future use)
-- =====================================================
CREATE TABLE IF NOT EXISTS pending_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(20) DEFAULT 'phonepe',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours')
);

-- Create indexes for pending payments
CREATE INDEX IF NOT EXISTS idx_pending_payments_customer_id ON pending_payments(customer_id);
CREATE INDEX IF NOT EXISTS idx_pending_payments_business_id ON pending_payments(business_id);
CREATE INDEX IF NOT EXISTS idx_pending_payments_status ON pending_payments(status);
CREATE INDEX IF NOT EXISTS idx_pending_payments_expires_at ON pending_payments(expires_at);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =====================================================

-- Function to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for customers table
CREATE TRIGGER update_customers_updated_at 
    BEFORE UPDATE ON customers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Triggers for businesses table
CREATE TRIGGER update_businesses_updated_at 
    BEFORE UPDATE ON businesses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Triggers for customer_credits table
CREATE TRIGGER update_customer_credits_updated_at 
    BEFORE UPDATE ON customer_credits 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SAMPLE DATA (Optional - Remove if not needed)
-- =====================================================

-- Insert sample customer (password should be hashed in real implementation)
-- INSERT INTO customers (name, phone, password) VALUES 
-- ('John Doe', '9876543210', 'hashed_password_here')
-- ON CONFLICT (phone) DO NOTHING;

-- Insert sample business (password and access_pin should be hashed/secure in real implementation)
-- INSERT INTO businesses (name, phone, password, access_pin, address) VALUES 
-- ('Sample Store', '9876543211', 'hashed_password_here', '1234', '123 Main Street')
-- ON CONFLICT (phone) DO NOTHING;

-- =====================================================
-- VIEWS FOR COMMON QUERIES (Optional)
-- =====================================================

-- View for customer transaction history with business names
CREATE OR REPLACE VIEW customer_transaction_history AS
SELECT 
    t.id,
    t.customer_id,
    t.business_id,
    b.name AS business_name,
    t.transaction_type,
    t.amount,
    t.notes,
    t.created_at
FROM transactions t
JOIN businesses b ON t.business_id = b.id
ORDER BY t.created_at DESC;

-- View for customer credit balances with business names
CREATE OR REPLACE VIEW customer_credit_balances AS
SELECT 
    cc.customer_id,
    cc.business_id,
    b.name AS business_name,
    cc.balance,
    cc.updated_at
FROM customer_credits cc
JOIN businesses b ON cc.business_id = b.id
WHERE cc.balance != 0
ORDER BY cc.updated_at DESC;

-- =====================================================
-- UTILITY FUNCTIONS (Optional)
-- =====================================================

-- Function to get customer's total credit across all businesses
CREATE OR REPLACE FUNCTION get_customer_total_credit(customer_uuid UUID)
RETURNS DECIMAL(10, 2) AS $$
BEGIN
    RETURN COALESCE((
        SELECT SUM(balance) 
        FROM customer_credits 
        WHERE customer_id = customer_uuid
    ), 0.00);
END;
$$ LANGUAGE plpgsql;

-- Function to get customer's credit with a specific business
CREATE OR REPLACE FUNCTION get_customer_business_credit(customer_uuid UUID, business_uuid UUID)
RETURNS DECIMAL(10, 2) AS $$
BEGIN
    RETURN COALESCE((
        SELECT balance 
        FROM customer_credits 
        WHERE customer_id = customer_uuid AND business_id = business_uuid
    ), 0.00);
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- PERMISSIONS (Adjust according to your setup)
-- =====================================================

-- Grant permissions to your application user (replace 'your_app_user' with actual username)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_app_user;

-- =====================================================
-- COMPLETED SETUP
-- =====================================================

-- Display success message
DO $$
BEGIN
    RAISE NOTICE 'KhataPe Customer Application database setup completed successfully!';
    RAISE NOTICE 'Tables created: customers, businesses, transactions, customer_credits, pending_payments';
    RAISE NOTICE 'Views created: customer_transaction_history, customer_credit_balances';
    RAISE NOTICE 'Functions created: get_customer_total_credit, get_customer_business_credit';
END $$;
