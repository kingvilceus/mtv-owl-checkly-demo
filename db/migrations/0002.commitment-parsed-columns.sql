-- Expand: add commitment_cents + currency alongside the raw commitment text.
-- The raw column stays so Step 1 instances keep working during a rolling deploy.
-- Parsing lives in one place (parse_commitment); a trigger keeps the derived
-- columns in sync on every write, and the UPDATE below backfills existing rows.

-- noqa: disable=all
CREATE FUNCTION parse_commitment(raw text)
RETURNS TABLE (commitment_cents bigint, currency char(3))
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    s text := trim(raw);
    code text;
    amount text;
BEGIN
    commitment_cents := NULL;
    currency := NULL;

    -- Not reported / Undisclosed / TBD / blank -> (NULL, NULL)
    IF s IS NULL OR s = '' OR s !~ '[0-9]' THEN
        RETURN NEXT;
        RETURN;
    END IF;

    s := replace(s, '~', '');

    -- currency: trailing 3-letter code, else leading code, else symbol
    code := upper((regexp_match(s, '([A-Za-z]{3})\s*$'))[1]);
    IF code IS NULL THEN
        code := upper((regexp_match(s, '^\s*([A-Za-z]{3})'))[1]);
    END IF;
    IF code IS NULL OR code NOT IN ('USD', 'GBP', 'EUR', 'JPY') THEN
        code := CASE
            WHEN position('$' IN s) > 0 THEN 'USD'
            WHEN position('£' IN s) > 0 THEN 'GBP'
            WHEN position('€' IN s) > 0 THEN 'EUR'
            WHEN position('¥' IN s) > 0 THEN 'JPY'
        END;
    END IF;

    -- amount: keep digits and the decimal point, then x100 (uniform, incl. JPY)
    amount := regexp_replace(s, '[^0-9.]', '', 'g');
    IF amount = '' OR amount = '.' THEN
        RETURN NEXT;
        RETURN;
    END IF;

    commitment_cents := round(amount::numeric * 100);
    currency := code;
    RETURN NEXT;
END;
$$;

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

ALTER TABLE funds
ADD COLUMN commitment_cents bigint,
ADD COLUMN currency char(3);

CREATE TRIGGER funds_sync_commitment
BEFORE INSERT OR UPDATE OF commitment ON funds
FOR EACH ROW
EXECUTE FUNCTION funds_sync_commitment();

UPDATE funds AS f
SET (commitment_cents, currency) = (
    SELECT
        p.commitment_cents,
        p.currency
    FROM parse_commitment(f.commitment) AS p
);
