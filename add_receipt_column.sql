-- Add receipt_image_url column to existing transactions table
-- Run this SQL command in your PostgreSQL database

ALTER TABLE transactions ADD COLUMN IF NOT EXISTS receipt_image_url TEXT;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS media_url TEXT;

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_transactions_receipt_image ON transactions(receipt_image_url) WHERE receipt_image_url IS NOT NULL;

-- Verify the column was added
-- \d transactions
