# Tableau build guide

No Tableau install was available while building FiberLens, so there is no `.twb` or `.twbx` in this repository. `python -m fiberlens` writes the flat extracts in `out/tableau/`; this guide says exactly what to build from them and what numbers each view must reproduce, so the finished workbook can be checked against `docs/REPORT.md`. The PNGs in `docs/previews/` are matplotlib drawings of the intended layout, not Tableau output.

## Requirements gathered from the stakeholder questions

| Audience | Question | View | Must match |
| --- | --- | --- | --- |
| VP Marketing | Which channels are efficient, and did mail work? | Campaign effectiveness | Cost per sign-up by channel (REPORT.md table); mail lift +8.8 percent |
| Broadband GM | Did something break last month? | Executive scorecard | Week 38 flagged, TX named as the cause |
| Strategy | Where do we expand? | Market opportunity | 352 Tier A counties; ten largest outside the footprint |
| All | Can I trust the numbers? | Data quality strip on each dashboard | Row counts and as-of vintages shown |

## Data connections (all CSV extracts, refreshed by `make report`)

| Extract | Grain | Used by |
| --- | --- | --- |
| `exec_scorecard_weekly.csv` | week | Scorecard |
| `channel_performance.csv` | channel | Campaign effectiveness |
| `lift_weekly.csv` | group x week | Campaign effectiveness |
| `market_opportunity.csv` | county | Market opportunity |
| `state_rollup.csv` | state | Market opportunity |
| `competitive_markets.csv` | footprint market | Campaign effectiveness (scatter) |

No joins are needed: each extract is already at the grain of its view, which keeps Tableau from fanning rows out (the failure behind INC-2).

## Calculated fields

```
Cost per sign-up        = SUM([spend]) / SUM([signups])          // never AVG of a ratio (INC-6)
Weighted availability   = SUM([avail] * [pop]) / SUM([pop])      // population weighted, not AVG([avail]) (INC-4)
Unrealized demand       = [pop] * MAX([avail] - [usage], 0)
Orders per 10k people   = SUM([orders]) * 10000 / SUM([pop])
Spend per order         = SUM([spend]) / SUM([orders])
Mail lift (static)      = value from REPORT.md; the estimate comes from the pipeline, not from a Tableau calculation
Tier A flag             = [tier] = 'A'
```

Use the pipeline's `score` and `tier` as given. Re-deriving them in Tableau would duplicate business logic in a second place.

## Dashboard 1: Executive scorecard

KPI tiles (orders, MRR added, spend, cost per order) with prior-period change; a weekly line of `orders` with `anomaly_flag` as an orange mark and a tooltip naming the state that explains it; spend as bars under the line on a shared week axis. Filter: date range. Keep text to one sentence per tile.

## Dashboard 2: Campaign effectiveness

Left: horizontal bars of cost per sign-up sorted ascending, with a caption that this is last-touch cost, not causal return. Right: `orders_per_10k` by week for treated and holdout with the flight weeks (20 to 31) shaded and the lift estimate and interval in the title. Below: scatter of `comp_a` against `orders_per_10k` by market with a trend line, sized by population.

## Dashboard 3: Market opportunity

Filled state map by weighted `usage` with a toggle to weighted `avail`; a ranked table of Tier A counties (`in_footprint = false`) by unrealized demand; a scatter of availability against usage, sized by population, colored by tier. Parameter: the user can choose the minimum score.

## QA checklist before publishing

1. Row counts in each extract match `out/report.json` (`data` block).
2. Cost per sign-up for email is $625, for TV is $1,667.
3. Texas weighted availability is 95.8 percent and usage 66.1 percent.
4. Only week 38 is flagged.
5. Every chart title says whether the data is real or synthetic.

## Performance

All extracts are under 4,000 rows except `market_opportunity.csv` (about 3,100) and `lift_weekly.csv` (104), so live connections are fine; use extracts anyway so the workbook opens offline.
