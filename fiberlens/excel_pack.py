"""An Excel pack for the people who will not open Python.  Inputs are values; every derived number is a live formula."""
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from fiberlens.load import ROOT

HDR = PatternFill("solid", fgColor="14213D")
INP = PatternFill("solid", fgColor="FFF4D6")
PATH = os.path.join(ROOT, "out", "FiberLens_Analyst_Pack.xlsx")


def _head(ws, row, labels):
    for i, t in enumerate(labels, 1):
        c = ws.cell(row, i, t); c.font = Font(bold=True, color="FFFFFF"); c.fill = HDR
        c.alignment = Alignment(wrap_text=True, vertical="center")


def _widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def build_pack(con, report):
    wb = Workbook()
    ws = wb.active; ws.title = "Read me"
    for i, line in enumerate([
        "FiberLens analyst pack",
        "Yellow cells are inputs copied from the pipeline. Every other number on these sheets is a formula you can audit.",
        "Real data: Microsoft AI for Good county broadband (Oct 2020), JHU/Census population, BLS 2016 unemployment.",
        "Synthetic data: Northwind Broadband campaigns, orders, competitor shares and survey (fictional provider).",
        "Sheets: Channel (cost per sign-up), Lift (difference-in-differences), Opportunity (county score), Survey (weighting), Scorecard (weekly trend)."], 1):
        ws.cell(i, 1, line).font = Font(bold=(i == 1), size=14 if i == 1 else 11)
    ws.column_dimensions["A"].width = 130

    # Channel
    ws = wb.create_sheet("Channel")
    _head(ws, 1, ["Channel", "Spend ($)", "Last-touch sign-ups", "Cost per sign-up ($)", "Share of spend", "Cost rank (1 = cheapest)"])
    ch = [c for c in report["channels"] if c["channel"] != "organic"]
    for r, c in enumerate(ch, 2):
        ws.cell(r, 1, c["channel"]); ws.cell(r, 2, c["spend"]).fill = INP; ws.cell(r, 3, c["signups"]).fill = INP
        ws.cell(r, 4, f"=B{r}/C{r}"); ws.cell(r, 5, f"=B{r}/SUM($B$2:$B${len(ch) + 1})")
        ws.cell(r, 6, f"=RANK(D{r},$D$2:$D${len(ch) + 1},1)")
    t = len(ch) + 2
    ws.cell(t, 1, "Total").font = Font(bold=True); ws.cell(t, 2, f"=SUM(B2:B{t - 1})"); ws.cell(t, 3, f"=SUM(C2:C{t - 1})"); ws.cell(t, 4, f"=B{t}/C{t}")
    for r in range(2, t + 1):
        ws.cell(r, 2).number_format = '#,##0'; ws.cell(r, 3).number_format = '#,##0'; ws.cell(r, 4).number_format = '#,##0.00'; ws.cell(r, 5).number_format = '0.0%'
    _widths(ws, [16, 16, 20, 20, 14, 22])

    # Lift
    ws = wb.create_sheet("Lift")
    arr = con.execute("""
        select e.grp, sum(case when w.week between 1 and 19 then w.orders end) pre, sum(case when w.week between 20 and 31 then w.orders end) fl,
               sum(w.pop) / 52.0 pop from fct_market_week w join stg_experiment e on e.fips = w.fips group by e.grp""").df().set_index("grp")
    _head(ws, 1, ["Item", "Treated", "Holdout"])
    rows = [("Market population (sum)", arr.loc["treated", "pop"], arr.loc["holdout", "pop"]), ("Orders, weeks 1 to 19", arr.loc["treated", "pre"], arr.loc["holdout", "pre"]),
            ("Orders, weeks 20 to 31 (flight)", arr.loc["treated", "fl"], arr.loc["holdout", "fl"]), ("Weeks before flight", 19, 19), ("Flight weeks", 12, 12)]
    for r, (lab, a, b) in enumerate(rows, 2):
        ws.cell(r, 1, lab); ws.cell(r, 2, float(a)).fill = INP; ws.cell(r, 3, float(b)).fill = INP
    ws.cell(7, 1, "Pre rate (orders per 10k per week)"); ws.cell(8, 1, "Flight rate (orders per 10k per week)")
    for col in "BC":
        ws[f"{col}7"] = f"={col}3/({col}2*{col}5)*10000"; ws[f"{col}8"] = f"={col}4/({col}2*{col}6)*10000"
    ws["A10"] = "Naive lift (flight rate, treated vs holdout)"; ws["B10"] = "=B8/C8-1"
    ws["A11"] = "Difference-in-differences (log scale)"; ws["B11"] = "=LN(B8/B7)-LN(C8/C7)"
    ws["A12"] = "Lift estimate = EXP(DiD) - 1"; ws["B12"] = "=EXP(B11)-1"
    ws["A13"] = "95% interval from the bootstrap (static values)"; ws["B13"] = report["lift"]["ci_low"]; ws["C13"] = report["lift"]["ci_high"]
    ws["A14"] = "True simulated lift (known only because the data is synthetic)"; ws["B14"] = report["lift"]["true"]
    for r in (10, 12, 13, 14):
        for col in "BC":
            ws[f"{col}{r}"].number_format = '0.0%'
    for r in range(2, 7):
        for col in "BC":
            ws[f"{col}{r}"].number_format = '#,##0'
    for col in "BC":
        for r in (7, 8):
            ws[f"{col}{r}"].number_format = '0.000'
    _widths(ws, [60, 16, 16])

    # Opportunity
    ws = wb.create_sheet("Opportunity")
    ws["A1"] = "Weights"; ws["B1"] = "Gap"; ws["C1"] = "Availability"; ws["D1"] = "Size"; ws["E1"] = "Low unemployment"; ws["F1"] = "Tier A cutoff"; ws["G1"] = "Tier B cutoff"
    for col, v in zip("BCDEFG", [0.40, 0.25, 0.20, 0.15, 0.80, 0.55]):
        ws[f"{col}2"] = v; ws[f"{col}2"].fill = INP
    ws["A2"] = "Change a weight and the scores and tiers below recalculate."
    _head(ws, 4, ["FIPS", "County", "State", "Population", "Availability", "Usage", "Unemployment 2016 (%)", "Unrealized-demand headcount",
                  "Rank: gap", "Rank: availability", "Rank: size", "Rank: unemployment", "Score", "Tier", "Pipeline score", "Check (diff)"])
    top = con.execute("select fips, county_name, st, pop, avail, usage, unemp_2016, pr_gap, pr_avail, pr_pop, pr_unemp, score from mart_opportunity_score order by score desc, pop desc limit 100").df()
    for r, row in enumerate(top.itertuples(index=False), 5):
        ws.cell(r, 1, row.fips); ws.cell(r, 2, row.county_name); ws.cell(r, 3, row.st)
        for c, v in zip(range(4, 8), [row.pop, row.avail, row.usage, row.unemp_2016]):
            ws.cell(r, c, None if v != v else float(v)).fill = INP
        ws.cell(r, 8, f"=D{r}*MAX(E{r}-F{r},0)")
        for c, v in zip(range(9, 13), [row.pr_gap, row.pr_avail, row.pr_pop, row.pr_unemp]):
            ws.cell(r, c, float(v)).fill = INP
        ws.cell(r, 13, f"=ROUND($B$2*I{r}+$C$2*J{r}+$D$2*K{r}+$E$2*(1-IF(G{r}=\"\",0.5,L{r})),4)")
        ws.cell(r, 14, f"=IF(M{r}>=$F$2,\"A\",IF(M{r}>=$G$2,\"B\",\"C\"))")
        ws.cell(r, 15, float(row.score)).fill = INP
        ws.cell(r, 16, f"=M{r}-O{r}")
        ws.cell(r, 4).number_format = '#,##0'; ws.cell(r, 8).number_format = '#,##0'
    _widths(ws, [9, 24, 7, 13, 12, 9, 14, 16, 9, 12, 9, 12, 9, 7, 12, 11])
    ws.freeze_panes = "A5"

    # Survey
    ws = wb.create_sheet("Survey")
    _head(ws, 1, ["Age band", "Population share", "Respondents", "Sample share", "Weight", "Mean intent (1 to 5)"])
    df = con.execute("select age_band, count(*) n, avg(intent) m from stg_survey group by age_band order by age_band").df()
    shares = {"18-34": 0.30, "35-54": 0.35, "55+": 0.35}
    for r, row in enumerate(df.itertuples(index=False), 2):
        ws.cell(r, 1, row.age_band); ws.cell(r, 2, shares[row.age_band]).fill = INP; ws.cell(r, 3, int(row.n)).fill = INP
        ws.cell(r, 4, f"=C{r}/SUM($C$2:$C$4)"); ws.cell(r, 5, f"=B{r}/D{r}"); ws.cell(r, 6, float(row.m)).fill = INP
    ws["A6"] = "Unweighted mean intent"; ws["B6"] = "=SUMPRODUCT(C2:C4,F2:F4)/SUM(C2:C4)"
    ws["A7"] = "Weighted mean intent"; ws["B7"] = "=SUMPRODUCT(B2:B4,F2:F4)"
    ws["A8"] = "Bias removed by weighting"; ws["B8"] = "=B6-B7"
    for r in range(2, 5):
        ws.cell(r, 2).number_format = '0%'; ws.cell(r, 4).number_format = '0.0%'; ws.cell(r, 5).number_format = '0.000'; ws.cell(r, 6).number_format = '0.000'
    for r in (6, 7, 8):
        ws[f"B{r}"].number_format = '0.000'
    _widths(ws, [28, 18, 14, 14, 10, 20])

    # Scorecard
    ws = wb.create_sheet("Scorecard")
    _head(ws, 1, ["Week", "Week start", "Orders", "Spend ($)", "Cost per order ($)", "Prior 4-week average", "Vs prior average", "Flag (more than 10 percent off)"])
    sc = con.execute("select week, week_start, orders, spend from mart_weekly_scorecard order by week").df()
    for r, row in enumerate(sc.itertuples(index=False), 2):
        ws.cell(r, 1, int(row.week)); ws.cell(r, 2, str(row.week_start)[:10]); ws.cell(r, 3, int(row.orders)).fill = INP; ws.cell(r, 4, float(row.spend)).fill = INP
        ws.cell(r, 5, f"=D{r}/C{r}")
        if r >= 6:
            ws.cell(r, 6, f"=AVERAGE(C{r - 4}:C{r - 1})"); ws.cell(r, 7, f"=C{r}/F{r}-1"); ws.cell(r, 8, f"=IF(ABS(G{r})>0.1,\"CHECK\",\"\")")
            ws.cell(r, 7).number_format = '0.0%'
        ws.cell(r, 4).number_format = '#,##0'; ws.cell(r, 5).number_format = '#,##0.00'; ws.cell(r, 6).number_format = '#,##0'
    _widths(ws, [8, 12, 10, 14, 16, 18, 16, 28]); ws.freeze_panes = "A2"
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    wb.save(PATH)
    return PATH
