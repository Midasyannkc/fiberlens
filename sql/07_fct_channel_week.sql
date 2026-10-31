CREATE TABLE fct_channel_week AS
WITH s AS (SELECT fips, week, channel, sum(spend) AS spend FROM stg_spend GROUP BY ALL),
     a AS (SELECT fips, week, channel, count(*) AS signups, sum(monthly_price) AS mrr FROM attributed_orders GROUP BY ALL)
SELECT coalesce(s.fips, a.fips) AS fips, coalesce(s.week, a.week) AS week, coalesce(s.channel, a.channel) AS channel,
       coalesce(s.spend, 0) AS spend, coalesce(a.signups, 0) AS signups, coalesce(a.mrr, 0) AS mrr
FROM s FULL JOIN a ON s.fips = a.fips AND s.week = a.week AND s.channel = a.channel;
