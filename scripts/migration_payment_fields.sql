-- Agregar campos de método de pago y comprobante a debt_payments
ALTER TABLE debt_payments ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50);
ALTER TABLE debt_payments ADD COLUMN IF NOT EXISTS voucher_filename VARCHAR(255);
ALTER TABLE debt_payments ADD COLUMN IF NOT EXISTS voucher_path VARCHAR(512);
