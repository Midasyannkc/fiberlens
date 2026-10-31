-- Cost per signup is total spend over total sign-ups.  Averaging spend/signups per market-week would weight a
-- one-signup week the same as a hundred-signup week and silently drop weeks with spend but no signups.
CREATE TABLE mart_channel_performance AS
SELECT channel, sum(spend) AS spend, sum(signups) AS signups, sum(mrr) AS mrr,
       CASE WHEN sum(spend) > 0 THEN sum(spend) / nullif(sum(signups), 0) END AS cost_per_signup
FROM fct_channel_week
GROUP BY channel;
