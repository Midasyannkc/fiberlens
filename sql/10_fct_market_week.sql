CREATE TABLE fct_market_week AS
SELECT m.fips, m.st, m.pop, w.week, count(o.order_id) AS orders
FROM stg_markets m
CROSS JOIN (SELECT unnest(range(1, 53)) AS week) w
LEFT JOIN stg_orders o ON o.fips = m.fips AND o.week = w.week
GROUP BY ALL;
