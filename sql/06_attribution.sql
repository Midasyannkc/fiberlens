-- Credit each order to a marketing channel. Orders with no touch in the prior 28 days are 'organic'.
CREATE TABLE attributed_orders AS
SELECT o.order_id, o.fips, o.week, o.monthly_price, t.channel
FROM stg_orders o
JOIN stg_touches t ON t.order_id = o.order_id
UNION ALL
SELECT o.order_id, o.fips, o.week, o.monthly_price, 'organic'
FROM stg_orders o
WHERE NOT EXISTS (SELECT 1 FROM stg_touches t WHERE t.order_id = o.order_id);
