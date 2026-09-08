-- Best effort: the raw commitment text can't be reconstructed from cents +
-- currency, so the restored column comes back empty. The sync trigger is
-- recreated so future writes to `commitment` keep the parsed columns in step.

ALTER TABLE funds
ADD COLUMN commitment text;

-- noqa: disable=all
CREATE FUNCTION funds_sync_commitment()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    SELECT p.commitment_cents, p.currency
    INTO NEW.commitment_cents, NEW.currency
    FROM parse_commitment(NEW.commitment) AS p;
    RETURN NEW;
END;
$$;
-- noqa: enable=all

CREATE TRIGGER funds_sync_commitment
BEFORE INSERT OR UPDATE OF commitment ON funds
FOR EACH ROW
EXECUTE FUNCTION funds_sync_commitment();
