-- Add missing purchase_price column to equipment table
ALTER TABLE IF EXISTS equipment
ADD COLUMN IF NOT EXISTS purchase_price DECIMAL(10, 2);

-- Add comment
COMMENT ON COLUMN equipment.purchase_price IS 'Purchase price of the equipment';
