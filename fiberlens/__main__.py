"""python -m fiberlens : build the pipeline, run every analysis, write the report, extracts, previews and Excel pack."""
from fiberlens import excel_pack, exports
from fiberlens.pipeline import build
from fiberlens.report import build_report, save
from fiberlens.writeup import write_report_md


def main():
    con = build()
    report = build_report(con)
    save(report)
    exports.write_extracts(con, report)
    exports.previews(con, report)
    excel_pack.build_pack(con, report)
    write_report_md(report)
    print("report written")


if __name__ == "__main__":
    main()
