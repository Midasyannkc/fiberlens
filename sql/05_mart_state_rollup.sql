-- State view for leadership: how much of the population can get broadband and how many use it.
CREATE TABLE mart_state_rollup AS
SELECT st, count(*) AS counties, sum(pop) AS pop,
       avg(avail) AS avail_fcc, avg(usage) AS usage_ms
FROM mart_market_opportunity
GROUP BY st;
