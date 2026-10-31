CREATE TABLE mart_channel_performance AS
SELECT channel, sum(spend) AS spend, sum(signups) AS signups, sum(mrr) AS mrr,
       avg(spend / nullif(signups, 0)) AS cost_per_signup
FROM fct_channel_week
GROUP BY channel;
