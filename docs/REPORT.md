# FiberLens report

All numbers below come from `python -m fiberlens`. Campaign, order, competitor and survey data are **synthetic** (a fictional provider, Northwind Broadband); county availability, usage, population and unemployment are **real**.

## What the business should take away

1. **Mail worked, but modestly, and the first read said it did not.** Direct mail lifted sign-ups in treated markets by +8.8% (95% interval +3.9% to +13.6%). The true simulated lift is +12.6%, inside that interval. A plain treated-versus-holdout comparison read -0.6% because the business had put mail in different kinds of markets (INC-5). At $1,329,872 spend that is about 1,060 extra orders, or $1,255 per incremental order, versus $1,199 per last-touch order.
2. **Cheapest channel is email ($625 per sign-up); most expensive is tv ($1,667).** Last-touch credit favors channels that sit late in the journey, so treat it as a ranking of attributed cost, not of causal return.
3. **Week 38 was an outage, not a demand problem.** Orders fell to 2,360 (robust z -4.2). TX explains 62% of the week-over-week change.
4. **Competitor coverage costs sign-ups.** A market fully covered by competitor A sells about 31% less than one it does not reach (log coefficient -0.37, 95% interval -0.47 to -0.28); for competitor B the figure is about 14%.
5. **Survey intent is 3.22 of 5 once weighted, not 3.40.** The panel over-represents under-35s, who are keener. Net promoter score is -30.0 weighted versus -19.2 raw.
6. **Where to look for new markets.** 352 counties score Tier A; the ten largest not already in the footprint are listed below.

## Channel economics (last touch, synthetic spend)

| Channel | Spend | Sign-ups credited | Cost per sign-up |
| --- | --- | --- | --- |
| email | $1,780,989 | 2,851 | $625 |
| search | $13,620,157 | 17,787 | $766 |
| door_to_door | $7,098,988 | 6,376 | $1,113 |
| direct_mail | $1,329,872 | 1,109 | $1,199 |
| social | $9,109,048 | 6,202 | $1,469 |
| tv | $5,419,085 | 3,251 | $1,667 |

Organic sign-ups (no marketing touch in the prior 28 days): 106,460 of 144,036 orders.

## White space: Tier A counties outside the footprint

Real data. Gap headcount is population times the share that can get broadband but does not use it.

| County | Population | Availability | Usage | Gap headcount | Score |
| --- | --- | --- | --- | --- | --- |
| Los Angeles County, CA | 10,039,107 | 99.6% | 73.4% | 2,625,226 | 0.882 |
| Cook County, IL | 5,150,233 | 99.2% | 63.7% | 1,828,848 | 0.842 |
| Harris County, TX | 4,713,325 | 94.7% | 70.8% | 1,125,542 | 0.807 |
| Kings County, NY | 2,559,903 | 99.8% | 56.8% | 1,100,246 | 0.883 |
| Maricopa County, AZ | 4,485,414 | 99.3% | 77.4% | 983,651 | 0.902 |
| Miami-Dade County, FL | 2,716,940 | 96.5% | 68.1% | 771,339 | 0.820 |
| San Diego County, CA | 3,338,330 | 98.1% | 76.1% | 733,431 | 0.867 |
| New York County, NY | 1,628,706 | 100.0% | 55.0% | 732,918 | 0.924 |
| Bronx County, NY | 1,418,207 | 98.2% | 48.6% | 703,005 | 0.800 |
| Queens County, NY | 2,253,858 | 100.0% | 68.9% | 700,048 | 0.920 |

## Data and limits

- Real: 3,142 counties, 328,242,507 people. Availability is FCC Form 477 as published by Microsoft AI for Good in Oct 2020 and is old; usage is Microsoft's estimate; unemployment is BLS 2016. Vintages differ and are not aligned. Nine counties lack availability, eleven lack usage; they are excluded from scoring, not guessed.
- Synthetic: 420 markets, 144,036 orders, 75,353 touches, $38,358,139 spend, 3,000 survey respondents. The true effects are known from `data/synthetic/truth.json`, so the analysis can be graded, but that also means these results show the method works, not that any real campaign performs this way.
- Attribution is last touch over a 28-day window. It is a convention, not truth.
- The competitor effect is estimated across markets and could be confounded in real data; here it is clean by construction.
- No Tableau workbook is included. The extracts in `out/tableau/` and the build guide in `docs/tableau_build_guide.md` describe what to build; the PNGs in `docs/previews/` are matplotlib drawings of the intended layout.
