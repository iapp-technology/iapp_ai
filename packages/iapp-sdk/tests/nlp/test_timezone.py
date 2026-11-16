"""The package must work on machines without a system time zone database."""

import os
import subprocess
import sys

CODE = """
import iapp_nlp
from iapp_nlp.util import thai_strptime
print(iapp_nlp.word_tokenize("สวัสดีครับ"), thai_strptime("15 ก.ค. 2565", "%d %B %Y").tzinfo)
"""


def test_imports_without_a_system_time_zone_database(tmp_path):
    # an empty PYTHONTZPATH hides /usr/share/zoneinfo, as on Alpine or distroless images
    env = {**os.environ, "PYTHONTZPATH": str(tmp_path)}
    result = subprocess.run([sys.executable, "-c", CODE], env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "['สวัสดี', 'ครับ'] Asia/Bangkok"
