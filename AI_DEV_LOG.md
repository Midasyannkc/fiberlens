# Development log

Built with an AI assistant (Claude) writing code and tests under direction; the author reviewed and committed the work. Notes on where the tool helped, where it was wrong, and what was checked.

## How the work was checked
- Every incident was written as a failing test first. `scripts/verify_incidents.py` re-runs both commits of each incident in clean worktrees.
- Analysis code was graded against `data/synthetic/truth.json`: true mail lift, outage week and state, survey population mean, competitor effects.
- The Excel pack was recalculated in LibreOffice and compared with the pipeline to 1e-9; no cell returned an error.
- The deck was rendered to images and inspected.

## Where the first attempt was wrong
- Planned the selection-bias incident as an overstated lift (about +25%). The data showed the opposite: treated markets had lower baseline sign-up rates (higher usage means less unmet demand), so the naive read was -0.6%. The incident was written from the measured numbers, not the plan.
- The planted outage first hid inside order noise (a 4.5 percent dip against 1.9 percent noise). It was made severe enough to detect and the detector gained a minimum relative-deviation rule so smooth series never flag.
- A first anomaly test was committed while failing because a chained shell command hid the pytest exit status. It was fixed in the next commit; the history shows it.
- The bootstrap interval changed between runs because DuckDB returned markets in a different order. Markets are now sorted before resampling.
- The real Microsoft file uses "-" for missing values, which turned numeric columns into text. They load as NULL now and a test counts them.
- Opportunity tiers first put 80 percent of the population in Tier A; the cutoff was raised until Tier A is the top 11 percent of counties.

## Things deliberately not done
- No Tableau workbook: no Tableau in the sandbox. Extracts and a build guide instead.
- No Redshift, Azure or Databricks: DuckDB stands in, and the README says so.
