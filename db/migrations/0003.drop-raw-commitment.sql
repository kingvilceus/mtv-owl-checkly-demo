-- Contract half of the expand/contract. The API stopped reading `commitment` in
-- Step 2, so once Step 2 is fully rolled out the raw column can go.
-- parse_commitment() stays -- seed.py uses it to load the CSV from here on.

DROP TRIGGER IF EXISTS funds_sync_commitment ON funds;
DROP FUNCTION IF EXISTS funds_sync_commitment();

ALTER TABLE funds
DROP COLUMN commitment;
