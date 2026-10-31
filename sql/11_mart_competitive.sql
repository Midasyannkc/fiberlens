CREATE TABLE mart_competitive AS
SELECT m.fips, m.st, m.county_name, m.pop, m.avail, m.usage, m.comp_a, m.comp_b,
       1 - (1 - m.comp_a) * (1 - m.comp_b) AS pressure,
       count(o.order_id) * 10000.0 / m.pop AS orders_per_10k
FROM stg_markets m
LEFT JOIN stg_orders o ON o.fips = m.fips
GROUP BY m.fips, m.st, m.county_name, m.pop, m.avail, m.usage, m.comp_a, m.comp_b;
