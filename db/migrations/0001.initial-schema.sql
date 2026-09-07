-- Baseline schema for the funds app.
-- commitment is stored as raw text exactly as it arrives in the CSV
-- (e.g. "$1,200,000 USD", "USD 10,000,000", "Not reported", ""); parsing is a
-- later migration. NULL is used for blank values.

CREATE TABLE funds (
    fund_id text PRIMARY KEY,
    fund_name text NOT NULL,
    manager text NOT NULL,
    strategy text NOT NULL,
    vintage_year integer NOT NULL,
    commitment text,
    reported_at date NOT NULL
);

CREATE INDEX funds_strategy_idx ON funds (strategy);
