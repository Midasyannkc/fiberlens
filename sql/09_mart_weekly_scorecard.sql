CREATE TABLE mart_weekly_scorecard AS
WITH o AS (SELECT week, count(*) AS orders, sum(monthly_price) AS mrr FROM stg_orders GROUP BY week),
     s AS (SELECT week, sum(spend) AS spend FROM stg_spend GROUP BY week)
SELECT o.week, DATE '2025-01-06' + CAST((o.week - 1) * 7 AS INTEGER) AS week_start, o.orders, o.mrr, s.spend,
       s.spend / o.orders AS cost_per_order,
       o.orders - lag(o.orders) OVER (ORDER BY o.week) AS wow_orders
FROM o JOIN s USING (week)
ORDER BY o.week;
