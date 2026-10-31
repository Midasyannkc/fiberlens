"""Build every table: real staging, synthetic staging, then the SQL models in sql/ in filename order."""
import glob
import os

from fiberlens.load import ROOT, connect
from fiberlens.synth import load_synthetic

SQL_DIR = os.path.join(ROOT, "sql")


def build():
    con = load_synthetic(connect())
    for path in sorted(glob.glob(os.path.join(SQL_DIR, "*.sql"))):
        con.execute(open(path).read())
    return con
