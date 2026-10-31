-- State view for leadership: share of the population that can get broadband and share that use it.
-- Rates are weighted by county population; a plain AVG would let a tiny rural county count as much as Houston.
-- Counties with a missing rate are left out of both the numerator and the weight.
CREATE TABLE mart_state_rollup AS
SELECT st, count(*) AS counties, sum(pop) AS pop,
       sum(avail * pop) / sum(CASE WHEN avail IS NOT NULL THEN pop END) AS avail_fcc,
       sum(usage * pop) / sum(CASE WHEN usage IS NOT NULL THEN pop END) AS usage_ms
FROM mart_market_opportunity
GROUP BY st;
