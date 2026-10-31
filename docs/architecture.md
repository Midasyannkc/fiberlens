# Architecture

```
data/raw (real, committed)           data/synthetic (generated, git-ignored)
  Microsoft county + ZIP broadband     markets, spend, orders, touches,
  JHU/Census population                survey, experiment assignment,
  BLS 2016 unemployment                truth.json (known true effects)
        |                                      |
        v                                      v
 fiberlens/load.py  --- DuckDB raw_* ---  fiberlens/synth.py --- stg_*
        |                                      |
        +----------------- sql/01 ... 11 ------+
                                |
   stg_county -> mart_market_opportunity -> mart_opportunity_score -> mart_state_rollup
   stg_orders + stg_touches -> attributed_orders -> fct_channel_week -> mart_channel_performance
   stg_orders + stg_spend -> mart_weekly_scorecard, fct_market_week, mart_competitive
                                |
        fiberlens/{lift,survey,anomaly,competitive}.py
                                |
                       report.py -> out/report.json, docs/REPORT.md
                                |
         exports.py (Tableau extracts, previews)   excel_pack.py   deck/build_deck.js
```

## Grain of every model

| Model | One row per |
| --- | --- |
| stg_county, mart_market_opportunity, mart_opportunity_score | county |
| mart_state_rollup | state |
| attributed_orders | order |
| fct_channel_week | market, week, channel |
| mart_channel_performance | channel |
| mart_weekly_scorecard | week |
| fct_market_week | market, week |
| mart_competitive | footprint market |

## Design choices

- DuckDB in memory: the whole project rebuilds in seconds and needs no server.
- Known truth: because campaign data is simulated, `truth.json` records the true mail lift, the outage week and state, the survey population mean and the competitor effects. Tests grade the analysis against it, which real data would never allow.
- Selection bias on purpose: treated markets are drawn from the better-served half so a naive comparison fails, as it would in practice when sales teams choose where to run campaigns.
