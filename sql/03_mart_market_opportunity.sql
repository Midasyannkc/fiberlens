-- County grain. Adds how much of each county is "available but not using" (the unrealized-demand gap) and a summary of its ZIP-level usage.
-- ZIP rows are collapsed to one row per county BEFORE the join so county measures are never repeated.
CREATE TABLE mart_market_opportunity AS
SELECT c.fips, c.st, c.county_name, c.pop, c.avail, c.usage, c.unemp_2016,
       greatest(c.avail - c.usage, 0) AS gap,
       c.pop * greatest(c.avail - c.usage, 0) AS gap_pop,
       z.zip_count, z.zip_usage_min, z.zip_usage_max
FROM stg_county c
LEFT JOIN (
  SELECT fips, count(*) AS zip_count, min(zip_usage) AS zip_usage_min, max(zip_usage) AS zip_usage_max
  FROM stg_zip GROUP BY fips
) z ON z.fips = c.fips;
