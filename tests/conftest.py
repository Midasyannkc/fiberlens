import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
SYN = os.path.join(ROOT, "data", "synthetic")


@pytest.fixture(scope="session", autouse=True)
def synthetic_data():
    if not os.path.exists(os.path.join(SYN, "truth.json")):
        subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "gen_synthetic.py")], check=True)
    return SYN
