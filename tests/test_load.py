from fiberlens.load import connect


def test_row_counts_match_the_real_files():
    con = connect()
    n = lambda t: con.execute(f"select count(*) from {t}").fetchone()[0]
    assert n("raw_ms_county") == 3142
    assert n("raw_ms_zip") == 32735
    assert 3100 < n("raw_population") < 3300
    assert n("raw_unemployment") == 3219


def test_availability_and_usage_are_fractions():
    con = connect()
    lo, hi = con.execute("select min(least(avail,usage)), max(greatest(avail,usage)) from raw_ms_county").fetchone()
    assert 0 <= lo and hi <= 1.0


def test_zip_codes_are_five_characters():
    con = connect()
    assert con.execute("select count(*) from raw_ms_zip where length(zip) <> 5").fetchone()[0] == 0


def test_dash_placeholders_become_nulls_not_dropped_rows():
    con = connect()
    assert con.execute("select count(*) from raw_ms_county where avail is null").fetchone()[0] == 9
    assert con.execute("select count(*) from raw_ms_county where usage is null").fetchone()[0] == 11
