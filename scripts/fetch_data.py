"""Download the real public files FiberLens uses, record size, row count and sha256 in data/raw/MANIFEST.json."""
import hashlib, json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
GH = "https://raw.githubusercontent.com/"
SOURCES = {
    "ms_county.csv": (GH + "microsoft/USBroadbandUsagePercentages/master/dataset/broadband_data_2020October.csv",
                      "Microsoft AI for Good: county broadband availability (FCC Form 477) and usage, Oct 2020"),
    "ms_zip.csv": (GH + "microsoft/USBroadbandUsagePercentages/master/dataset/broadband_data_zipcode.csv",
                   "Microsoft AI for Good: ZIP-level broadband usage with error ranges"),
    "jhu_uid.csv": (GH + "CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv",
                    "JHU CSSE lookup table: county FIPS and population (US Census based)"),
    "bls_unemp_2016.csv": (GH + "plotly/datasets/master/fips-unemp-16.csv",
                           "BLS LAUS 2016 county unemployment rate, as published in the plotly datasets repo"),
}


def main():
    os.makedirs(RAW, exist_ok=True)
    manifest = {}
    for name, (url, what) in SOURCES.items():
        data = urllib.request.urlopen(url, timeout=60).read()
        open(os.path.join(RAW, name), "wb").write(data)
        manifest[name] = {"url": url, "what": what, "bytes": len(data), "lines": data.count(b"\n"),
                          "sha256": hashlib.sha256(data).hexdigest()}
        print(f"{name}: {len(data)} bytes")
    json.dump(manifest, open(os.path.join(RAW, "MANIFEST.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
