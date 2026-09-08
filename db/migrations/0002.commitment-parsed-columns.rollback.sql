DROP TRIGGER IF EXISTS funds_sync_commitment ON funds;
DROP FUNCTION IF EXISTS funds_sync_commitment();

ALTER TABLE funds
DROP COLUMN IF EXISTS commitment_cents,
DROP COLUMN IF EXISTS currency;

DROP FUNCTION IF EXISTS parse_commitment(text);
