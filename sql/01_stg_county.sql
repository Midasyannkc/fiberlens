-- One row per county: real availability and usage (Microsoft, Oct 2020), real population (JHU/Census), real 2016 unemployment (BLS).
CREATE TABLE stg_county AS
SELECT m.fips, m.st, m.county_name, p.pop, m.avail, m.usage, u.unemp_2016
FROM raw_ms_county m
JOIN raw_population p ON p.fips = m.fips
LEFT JOIN raw_unemployment u ON u.fips = m.fips;
