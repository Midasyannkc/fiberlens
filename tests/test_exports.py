import os
import shutil
import subprocess
import tempfile

import pandas as pd
import pytest
from openpyxl import load_workbook

from fiberlens import excel_pack, exports
from fiberlens.report import build_report
from tests.conftest import ROOT


@pytest.fixture(scope="module")
def report(con):
    return build_report(con)


def test_report_has_every_section(report):
    assert {"data", "scorecard", "anomalies", "root_cause", "channels", "lift", "competitive", "survey", "opportunity"} <= set(report)
    assert report["lift"]["ci_low"] <= report["lift"]["lift"] <= report["lift"]["ci_high"]


def test_tableau_extracts_have_the_columns_the_build_guide_uses(con, report):
    files = exports.write_extracts(con, report)
    assert set(files) == {"channel_performance.csv", "competitive_markets.csv", "exec_scorecard_weekly.csv", "lift_weekly.csv",
                          "market_opportunity.csv", "state_rollup.csv"}
    sc = pd.read_csv(os.path.join(exports.OUT, "exec_scorecard_weekly.csv"))
    assert len(sc) == 52 and sc.loc[sc.anomaly_flag, "week"].tolist() == [38]
    mo = pd.read_csv(os.path.join(exports.OUT, "market_opportunity.csv"), dtype={"fips": str})
    assert mo["fips"].str.len().eq(5).all() and mo["fips"].is_unique
    assert {"score", "tier", "in_footprint", "gap_pop"} <= set(mo.columns)


def test_excel_pack_derived_cells_are_formulas_not_pasted_values(con, report):
    path = excel_pack.build_pack(con, report)
    wb = load_workbook(path)
    assert wb["Lift"]["B12"].value.startswith("=EXP(")
    assert wb["Opportunity"]["M5"].value.startswith("=ROUND(")
    assert wb["Channel"]["D2"].value == "=B2/C2"
    assert wb["Survey"]["B7"].value == "=SUMPRODUCT(B2:B4,F2:F4)"


@pytest.mark.skipif(not shutil.which("soffice"), reason="LibreOffice not installed")
def test_excel_pack_recalculates_to_the_pipeline_numbers_with_no_errors(con, report):
    path = excel_pack.build_pack(con, report)
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", td, path], capture_output=True, timeout=180)
        wb = load_workbook(os.path.join(td, os.path.basename(path)), data_only=True)
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                assert not (isinstance(c.value, str) and c.value.startswith("#")), (ws.title, c.coordinate, c.value)
    assert abs(wb["Lift"]["B12"].value - report["lift"]["lift"]) < 1e-9
    assert abs(wb["Lift"]["B10"].value - report["lift"]["naive"]) < 1e-9
    assert max(abs(wb["Opportunity"].cell(r, 16).value) for r in range(5, 105)) < 1e-9
    assert abs(wb["Survey"]["B7"].value - report["survey"]["intent_weighted"]) < 1e-9


def test_saved_report_is_strict_json(report):
    import json
    from fiberlens.report import save
    save(report)
    json.loads(open(os.path.join(ROOT, "out", "report.json")).read(), parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
