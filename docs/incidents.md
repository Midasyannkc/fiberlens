# Incident log

Every incident has two commits. The first adds a test that fails for the right reason; a later one fixes the code and the same test passes. Hashes below come from `git log`.

| # | Incident | Found by | Reproduce | Fix |
| --- | --- | --- | --- | --- |
| INC-1 | Order credit was counted twice because every touch earned a full sign-up | a test that channel totals must equal orders | `94a5642` | `87cb715` |
| INC-2 | Joining ZIP rows to counties multiplied US population by 43 | a test that the county mart keeps one row per county and the same total population | `cf5665b` | `a7202d8` |
| INC-3 | Leading-zero FIPS codes silently dropped unemployment for 317 counties | a coverage test on the Alabama join | `8c90dad` | `f4ce7df` |
| INC-4 | State availability was a plain average of counties, so Texas looked 12 points worse than it is | an independent population-weighted recomputation from the county table | `6cc6a46` | `4602daf` |
| INC-5 | Comparing treated with holdout markets read the mail flight as no effect | a test that the lift estimate recovers the known simulated effect | `a1c2c1a` | `3197f08` |
| INC-6 | Cost per sign-up averaged ratios instead of dividing total spend by total sign-ups | a test that cost per sign-up equals spend over sign-ups for each channel | `6bd194a` | `c883031` |

### INC-1: Order credit was counted twice because every touch earned a full sign-up

The attribution model joined each order to all of its marketing touches, so an order touched by two channels was counted twice. 181,813 credited rows came from 144,036 orders, 26.2 percent too many, and the channel table summed to more than the business actually sold. Email was credited with 9,305 sign-ups and search with 28,071. The fix credits each order to its last touch in the prior 28 days; email falls to 2,851 and search to 17,787, and credited sign-ups plus organic now equal orders exactly.

Reproduce `94a5642`, fix `87cb715`. Found by: a test that channel totals must equal orders.

### INC-2: Joining ZIP rows to counties multiplied US population by 43

The market mart joined county rows to ZIP-level rows to carry ZIP usage detail, so each county repeated once per ZIP. The table grew from 3,142 counties to 32,741 rows and population summed to 14.2 billion instead of 328.2 million. Anything that summed population downstream, including state rollups and market sizing, inherited the error. The fix collapses ZIP rows to one row per county (count, minimum and maximum usage) before the join.

Reproduce `cf5665b`, fix `a7202d8`. Found by: a test that the county mart keeps one row per county and the same total population.

### INC-3: Leading-zero FIPS codes silently dropped unemployment for 317 counties

County keys were converted to plain integers on one side, so Alabama's 01001 became 1001 and never matched the BLS file, which keeps the zero. The join was a LEFT JOIN, so nothing failed: 317 of 3,142 counties (10.1 percent) simply lost their unemployment rate, concentrated in the seven states whose FIPS starts with 0 (AL, AK, AZ, AR, CA, CO, CT). The fix is one canonical 5-character zero-padded key used by every source; one county now has no rate, which is a real gap in the BLS file.

Reproduce `8c90dad`, fix `f4ce7df`. Found by: a coverage test on the Alabama join.

### INC-4: State availability was a plain average of counties, so Texas looked 12 points worse than it is

The state rollup used AVG over counties, letting a county of a few hundred people count as much as Harris County. Texas read 83.4 percent availability and 34.0 percent usage; weighted by population the figures are 95.8 and 66.1. The worst gap was Nevada at 32.7 points. The fix weights both rates by population and leaves counties with a missing rate out of the numerator and the denominator.

Reproduce `6cc6a46`, fix `4602daf`. Found by: an independent population-weighted recomputation from the county table.

### INC-5: Comparing treated with holdout markets read the mail flight as no effect

Mail went to better-served markets, which differ from the holdout markets before any campaign runs. Comparing their sign-up rates during the flight gave -0.6 percent (interval -9.8 to +8.0 percent), which would have ended the program, while the true simulated effect is +12.6 percent. The fix compares each group with its own pre-flight rate on a log scale (difference-in-differences) with a bootstrap over markets: +8.8 percent, interval +3.9 to +13.6 percent, which contains the truth.

Reproduce `a1c2c1a`, fix `3197f08`. Found by: a test that the lift estimate recovers the known simulated effect.

### INC-6: Cost per sign-up averaged ratios instead of dividing total spend by total sign-ups

The channel mart averaged spend divided by sign-ups across market-weeks. That weights a one-sign-up week like a hundred-sign-up week and drops every week with spend but no sign-ups. Email read $184 against a true $625, social $718 against $1,469, and TV $823 against $1,667, which would have moved budget toward the channels that looked cheapest. The fix divides total spend by total sign-ups and reports no cost for organic, which has no spend.

Reproduce `6bd194a`, fix `c883031`. Found by: a test that cost per sign-up equals spend over sign-ups for each channel.
