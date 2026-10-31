-- Credit each order to exactly one marketing channel using last touch: the most recent touch in the 28 days before the order.
-- Orders with no touch are 'organic'.
CREATE TABLE attributed_orders AS
SELECT o.order_id, o.fips, o.week, o.monthly_price, t.channel
FROM stg_orders o
JOIN (
  SELECT order_id, channel
  FROM (SELECT *, row_number() OVER (PARTITION BY order_id ORDER BY touch_date DESC, channel) AS rn FROM stg_touches)
  WHERE rn = 1
) t ON t.order_id = o.order_id
UNION ALL
SELECT o.order_id, o.fips, o.week, o.monthly_price, 'organic'
FROM stg_orders o
WHERE NOT EXISTS (SELECT 1 FROM stg_touches t WHERE t.order_id = o.order_id);
