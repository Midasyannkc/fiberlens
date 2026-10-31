# FiberLens

Broadband marketing analytics, built against the T-Mobile Senior Business Intelligence Analyst posting (Broadband Business Intelligence). It answers four questions a broadband business asks: which marketing channels are efficient, did a campaign actually work, where to grow, and which numbers can be trusted.

It is a portfolio project, not a product. County broadband, population and unemployment data are **real**. The provider (Northwind Broadband, fictional), its campaigns, orders, competitors and survey are **synthetic**, generated from a fixed seed with known true effects so the analysis can be graded. Every bug it hit is recorded as an incident with a failing-test commit and a separate fix commit.

## Results

All figures come from `python -m fiberlens` (see `docs/REPORT.md`).

| Area | Result |
| --- | --- |
| Campaign lift | Direct mail lifted sign-ups +8.8% (95% interval +3.9% to +13.6%) against a simulated truth of +12.6%. The naive treated-versus-holdout read was -0.6% |
| Channel economics | Last-touch cost per sign-up runs from $625 (email) to $1,667 (TV) on $38.4M of synthetic spend |
| Root cause | Week 38 is the only anomalous week of 52 (robust z -4.2); Texas explains 62% of the week-over-week drop |
| Competition | A market fully covered by competitor A sells about 31% less (interval from -0.47 to -0.28 on the log scale) |
| Survey | 3,000 respondents weighted to the population age mix: intent 3.22 of 5 against 3.40 unweighted; the weighted value recovers the simulated truth |
| Expansion | 352 of 3,122 scored counties are Tier A; the ten largest outside the footprint are listed in the report |
| Data quality | 3,142 real counties, 328,242,507 people; 9 counties lack availability and 11 lack usage and are excluded, not guessed |
| Deliverables | Tableau-ready extracts and build guide, three dashboard previews, a formula-driven Excel pack, a 10-slide executive deck |
| Incidents | 6, each a failing-test commit and a separate fix commit, re-run by `make verify` |

## How the posting maps to the code

| Posting responsibility | Where |
| --- | --- |
| Use data from several sources (Redshift, Azure, Databricks); guide data strategy and third-party data integration | `sql/` models over four real sources plus synthetic operational tables, joined on one canonical county key (`fiberlens/keys.py`). **Not used:** Redshift, Azure and Databricks themselves; the models run in DuckDB |
| Lead the analysis that drives customer experience and performance strategy | `docs/REPORT.md`, `fiberlens/{lift,competitive,survey}.py` |
| Early involvement defining reporting needs | Requirements table in `docs/tableau_build_guide.md` |
| Comprehensive dashboards for senior management | `out/tableau/` extracts, `docs/tableau_build_guide.md`, `docs/previews/`, `FiberLens_Executive_Summary.pptx` |
| Recommendations to cross-functional teams | Next-steps slide and the takeaways in `docs/REPORT.md` |
| Excel and PowerPoint | `out/FiberLens_Analyst_Pack.xlsx` (live formulas), the deck |
| Tableau, SQL for reporting and visualization | SQL in `sql/`; Tableau specified but **not built** (see limits) |
| Surveys, testing, competitive analysis, market research | `survey.py` (post-stratification), `lift.py` (difference-in-differences), `competitive.py` (regression with bootstrap) |

## Layout

```
fiberlens/   load, keys, synth, pipeline, lift, survey, anomaly, competitive, report, exports, excel_pack, writeup
sql/         11 models in dependency order, one grain each (docs/architecture.md)
scripts/     fetch_data, gen_synthetic, incidents, verify_incidents
tests/       46 tests, including the incident reproductions
deck/        build_deck.js for the executive summary
docs/        REPORT, architecture, tableau_build_guide, incident log, previews
data/raw/    the four real files with a sha256 manifest (committed)
```

## Run it

```
make install
make data      # fetch real files, generate the synthetic Northwind data (seeded, about 8 seconds)
make test      # 46 tests
make report    # report, Tableau extracts, previews, Excel pack
make deck      # needs Node and the pptxgenjs package
make verify    # re-runs every incident's reproduce and fix commits in clean worktrees
```

## Data sources

| File | What | Source |
| --- | --- | --- |
| `ms_county.csv`, `ms_zip.csv` | County broadband availability (FCC Form 477) and usage, ZIP usage | Microsoft AI for Good, Oct 2020, via raw.githubusercontent.com |
| `jhu_uid.csv` | County FIPS and population | JHU CSSE lookup table (Census based) |
| `bls_unemp_2016.csv` | County unemployment rate | BLS LAUS 2016, via the plotly datasets repo |

The FCC National Broadband Map and the Census API were blocked in the build environment, so the Microsoft files stand in for current FCC data; their availability figures are four years old. Source URLs, sizes and hashes are in `data/raw/MANIFEST.json`.

## Limits, stated plainly

- Campaigns, orders, touches, competitor footprint and survey are invented. The results show the methods work on data where the truth is known, not that any real campaign performs this way.
- No Tableau workbook exists. The extracts, calculated-field definitions and QA checklist are ready for one; the PNG previews are matplotlib drawings.
- Attribution is last touch over 28 days, a convention rather than truth. Only mail has an incrementality estimate.
- The mail estimate (+8.8%) is below the simulated truth (+12.6%) but inside its interval; with 180 markets the interval is wide.
- Availability, usage and unemployment come from different years (2020, 2020, 2016) and are not aligned.
- This is independent portfolio work with no production users and no real carrier data.

## Incidents

Every incident has two commits: one adds a test that fails for the right reason, a later one fixes the code and the same test passes. Detail is in `docs/incidents.md`.

<!-- incidents:start -->
| # | Incident | Found by | Reproduce | Fix |
| --- | --- | --- | --- | --- |
| INC-1 | Order credit was counted twice because every touch earned a full sign-up | a test that channel totals must equal orders | `b427d34` | `ce3182a` |
| INC-2 | Joining ZIP rows to counties multiplied US population by 43 | a test that the county mart keeps one row per county and the same total population | `0a342d6` | `ec2a1ec` |
| INC-3 | Leading-zero FIPS codes silently dropped unemployment for 317 counties | a coverage test on the Alabama join | `4159dc5` | `24a9c49` |
| INC-4 | State availability was a plain average of counties, so Texas looked 12 points worse than it is | an independent population-weighted recomputation from the county table | `2704ba7` | `7cb3233` |
| INC-5 | Comparing treated with holdout markets read the mail flight as no effect | a test that the lift estimate recovers the known simulated effect | `828facf` | `26747e3` |
| INC-6 | Cost per sign-up averaged ratios instead of dividing total spend by total sign-ups | a test that cost per sign-up equals spend over sign-ups for each channel | `8eb3dcd` | `c00f75e` |
<!-- incidents:end -->
