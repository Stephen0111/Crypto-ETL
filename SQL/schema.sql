CREATE TABLE IF NOT EXISTS `crypto-data-engineering.crypto.raw_prices` (
    symbol STRING,
    price FLOAT64,
    event_ts TIMESTAMP,
    payload STRING,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS `crypto-data-engineering.crypto.prices_hourly` (
    symbol STRING,
    price FLOAT64,
    price_ts TIMESTAMP,
    price_date DATE,
    price_hour INT64,
    source STRING
)
PARTITION BY price_date;

SELECT COUNT(*) FROM `crypto-data-engineering.crypto.prices_hourly`



