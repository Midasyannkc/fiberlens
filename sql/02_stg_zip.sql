CREATE TABLE stg_zip AS
SELECT fips, zip, usage AS zip_usage, ci95 FROM raw_ms_zip;
