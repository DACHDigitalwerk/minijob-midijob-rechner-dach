# -*- coding: utf-8 -*-
import pytest

from minijob_dach.models import (
    Country,
    EmploymentType,
    EmployerType,
    RVStatus,
)
from minijob_dach.gleitzone import (
    LOWER_LIMIT_2026,
    UPPER_LIMIT_2026,
    compute_factor_f,
    compute_assessment_basis_midijob,
)
from minijob_dach.calculator import calculate_minijob_midijob


def test_minijob_threshold_2026():
    assert LOWER_LIMIT_2026 == 556.00
    assert UPPER_LIMIT_2026 == 2000.00


def test_minijob_commercial_exempted():
    res = calculate_minijob_midijob(
        gross_wage=556.00,
        country=Country.DE,
        employer_type=EmployerType.COMMERCIAL,
        rv_status=RVStatus.EXEMPTED,
    )
    assert res.employment_type == EmploymentType.MINIJOB
    assert res.employee.net_wage == 556.00
    assert res.employee.total_deductions == 0.00
    assert res.employee.rv == 0.00
    # Employer levies: 15% KV (83.40) + 15% RV (83.40) + 2% Steuer (11.12)
    assert res.employer.kv == 83.40
    assert res.employer.rv == 83.40
    assert res.employer.flat_tax == 11.12
    assert not res.full_pension_entitlement


def test_minijob_commercial_mandatory_rv():
    # 3.6% employee pension contribution on 556.00 € = 20.02 €
    res = calculate_minijob_midijob(
        gross_wage=556.00,
        country=Country.DE,
        employer_type=EmployerType.COMMERCIAL,
        rv_status=RVStatus.MANDATORY,
    )
    assert res.employment_type == EmploymentType.MINIJOB
    assert res.employee.rv == 20.02
    assert res.employee.net_wage == 535.98
    assert res.full_pension_entitlement is True


def test_minijob_household_haushaltsscheck():
    # Household: 5% KV (27.80) + 5% RV (27.80) + 2% Steuer (11.12)
    res = calculate_minijob_midijob(
        gross_wage=556.00,
        country=Country.DE,
        employer_type=EmployerType.HOUSEHOLD,
        rv_status=RVStatus.EXEMPTED,
    )
    assert res.employer.kv == 27.80
    assert res.employer.rv == 27.80
    assert res.employer.flat_tax == 11.12
    assert res.tax_advantage_household_eur > 0.0  # § 35a EStG tax benefit


def test_midijob_assessment_basis():
    f = compute_factor_f()
    assert 0.65 <= f <= 0.72

    # At lower limit (556 €), B is close to F * 556
    b_min = compute_assessment_basis_midijob(556.01, f)
    assert b_min < 556.01

    # At 1200 €, B is less than 1200 €
    b_mid = compute_assessment_basis_midijob(1200.00, f)
    assert b_mid < 1200.00
    assert b_mid > 556.00

    # At upper limit (2000 €), B is exactly 2000.00 €
    b_max = compute_assessment_basis_midijob(2000.00, f)
    assert b_max == 2000.00


def test_midijob_calculation():
    res = calculate_minijob_midijob(
        gross_wage=1200.00,
        country=Country.DE,
        tax_class=1,
    )
    assert res.employment_type == EmploymentType.MIDIJOB
    assert res.full_pension_entitlement is True
    assert res.assessment_basis_employee < 1200.00
    assert res.employee.total_deductions > 0.0
    assert res.employee.net_wage > 900.00
    # Employer pays on full 1200 €
    assert res.employer.kv == round(1200.0 * ((0.146 + 0.017) / 2.0), 2)
    assert res.employer.rv == round(1200.0 * 0.093, 2)


def test_regular_employment_above_midijob():
    res = calculate_minijob_midijob(
        gross_wage=2500.00,
        country=Country.DE,
    )
    assert res.employment_type == EmploymentType.REGULAR
    assert res.assessment_basis_employee == 2500.00
    assert res.employee.rv == round(2500.0 * 0.093, 2)


def test_austria_geringfuegig():
    res = calculate_minijob_midijob(
        gross_wage=500.00,
        country=Country.AT,
    )
    assert res.employment_type == EmploymentType.MINIJOB
    assert res.employee.net_wage == 500.00
    assert res.employer.accident_insurance == round(500.0 * 0.011, 2)  # 1.1% UV


def test_austria_above_geringfuegig():
    res = calculate_minijob_midijob(
        gross_wage=1500.00,
        country=Country.AT,
    )
    assert res.employment_type == EmploymentType.REGULAR
    assert res.employee.total_social_security > 0.0


def test_switzerland_geringfuegig_and_regular():
    # 150 CHF per month (1,800 CHF / year < 2,300 CHF)
    res_ch_low = calculate_minijob_midijob(
        gross_wage=150.00,
        country=Country.CH,
        employer_type=EmployerType.COMMERCIAL,
    )
    assert res_ch_low.employment_type == EmploymentType.MINIJOB
    assert res_ch_low.employee.net_wage == 150.00

    # 1,000 CHF per month (> 2,300 CHF / year)
    res_ch_high = calculate_minijob_midijob(
        gross_wage=1000.00,
        country=Country.CH,
    )
    assert res_ch_high.employment_type == EmploymentType.REGULAR
    assert res_ch_high.employee.rv == round(1000.0 * 0.053, 2)  # AHV/IV/EO
