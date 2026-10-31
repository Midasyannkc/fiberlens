-- County grain. Adds how much of each county is "available but not using" (the unrealized-demand gap) and ZIP-level detail.
CREATE TABLE mart_market_opportunity AS
SELECT c.fips, c.st, c.county_name, c.pop, c.avail, c.usage, c.unemp_2016,
       greatest(c.avail - c.usage, 0) AS gap,
       c.pop * greatest(c.avail - c.usage, 0) AS gap_pop,
       z.zip, z.zip_usage
FROM stg_county c
LEFT JOIN stg_zip z ON z.fips = c.fips;
