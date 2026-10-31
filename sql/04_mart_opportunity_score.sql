-- Opportunity score in [0,1]: 40% unrealized-demand headcount, 25% availability, 20% market size, 15% low unemployment.
-- Counties missing availability or usage are left out rather than scored on a guess.
CREATE TABLE mart_opportunity_score AS
WITH r AS (
  SELECT *,
         percent_rank() OVER (ORDER BY gap_pop) AS pr_gap,
         percent_rank() OVER (ORDER BY avail) AS pr_avail,
         percent_rank() OVER (ORDER BY pop) AS pr_pop,
         percent_rank() OVER (ORDER BY unemp_2016) AS pr_unemp
  FROM mart_market_opportunity
  WHERE avail IS NOT NULL AND usage IS NOT NULL
)
SELECT *,
       round(0.40 * pr_gap + 0.25 * pr_avail + 0.20 * pr_pop
             + 0.15 * (1 - CASE WHEN unemp_2016 IS NULL THEN 0.5 ELSE pr_unemp END), 4) AS score,
       CASE WHEN 0.40 * pr_gap + 0.25 * pr_avail + 0.20 * pr_pop + 0.15 * (1 - CASE WHEN unemp_2016 IS NULL THEN 0.5 ELSE pr_unemp END) >= 0.70 THEN 'A'
            WHEN 0.40 * pr_gap + 0.25 * pr_avail + 0.20 * pr_pop + 0.15 * (1 - CASE WHEN unemp_2016 IS NULL THEN 0.5 ELSE pr_unemp END) >= 0.45 THEN 'B'
            ELSE 'C' END AS tier
FROM r;
