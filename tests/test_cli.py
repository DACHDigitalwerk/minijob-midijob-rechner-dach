# -*- coding: utf-8 -*-
import json
import os
import subprocess
import sys

CLI_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "minijob_dach", "cli.py"))


def test_cli_help():
    cmd = [sys.executable, CLI_PATH, "--help"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "dach-midijob" in res.stdout
    assert "--wage" in res.stdout


def test_cli_minijob():
    cmd = [
        sys.executable,
        CLI_PATH,
        "--wage", "556",
        "--rv-exempt",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "MINIJOB" in res.stdout
    assert "556.00" in res.stdout
    assert "AUSZAHLUNGSBETRAG (NETTO):       556.00" in res.stdout


def test_cli_midijob_json():
    cmd = [
        sys.executable,
        CLI_PATH,
        "--wage", "1200",
        "--json",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["gross_wage"] == 1200.0
    assert data["employment_type"] == "MIDIJOB"
    assert data["full_pension_entitlement"] is True
    assert "assessment_basis_employee" in data
