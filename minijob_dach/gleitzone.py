# -*- coding: utf-8 -*-
"""
Statutory Transitional Zone (Übergangsbereich / Gleitzone) calculation engine 2026.
Based on § 20 SGB IV, § 70 Abs. 1a SGB VI, and official factor F.
"""

from typing import Tuple


LOWER_LIMIT_2026 = 556.00      # Minijob-Höchstgrenze ab 2025/2026
UPPER_LIMIT_2026 = 2000.00     # Obergrenze des Übergangsbereichs

# Standard contribution rates (2026)
RATE_KV_BASE = 0.146           # 14.6% allgemeiner Beitragssatz KV
RATE_KV_ADDITIONAL_AVG = 0.017 # 1.7% durchschnittlicher Zusatzbeitrag
RATE_RV = 0.186                # 18.6% Rentenversicherung
RATE_AV = 0.026                # 2.6% Arbeitslosenversicherung
RATE_PV_BASE = 0.040           # 4.0% Pflegeversicherung Basis (2.0% AG, 2.0% AN)
RATE_PV_CHILDLESS = 0.006      # 0.6% Kinderlosenzuschlag für AN (ab 23 Jahren)


def compute_factor_f(additional_kv_rate: float = RATE_KV_ADDITIONAL_AVG) -> float:
    """
    Computes Factor F (§ 20 Abs. 2 SGB IV):
    F = 28% / Gesamtsozialversicherungsbeitragssatz
    """
    total_rate = RATE_KV_BASE + additional_kv_rate + RATE_RV + RATE_AV + RATE_PV_BASE
    # Statutory lump sum employer rate in minijobs is 28% (15% KV + 13% RV or average)
    return round(0.28 / total_rate, 4)


def compute_assessment_basis_midijob(
    gross_wage: float,
    factor_f: float,
    lower_limit: float = LOWER_LIMIT_2026,
    upper_limit: float = UPPER_LIMIT_2026,
) -> float:
    """
    Computes the fictitious reduced assessment basis B for employee contributions (§ 20 Abs. 2a SGB IV):
    B = F * G_unten + [ (G_oben / (G_oben - G_unten)) - (G_unten / (G_oben - G_unten)) * F ] * (E - G_unten)
    """
    if gross_wage <= lower_limit:
        return 0.0
    if gross_wage >= upper_limit:
        return gross_wage

    span = upper_limit - lower_limit
    term1 = factor_f * lower_limit
    term2 = ((upper_limit / span) - (lower_limit / span) * factor_f) * (gross_wage - lower_limit)

    b = term1 + term2
    return round(min(gross_wage, max(0.0, b)), 2)


def calculate_midijob_social_security(
    gross_wage: float,
    additional_kv_rate: float = RATE_KV_ADDITIONAL_AVG,
    has_children: bool = True,
    child_count: int = 1,
) -> Tuple[float, float, float, float, float, float, float, float]:
    """
    Calculates detailed social security contributions for employee and employer in the Übergangsbereich.
    Returns: (an_kv, an_rv, an_av, an_pv, ag_kv, ag_rv, ag_av, ag_pv)
    """
    f = compute_factor_f(additional_kv_rate)
    b = compute_assessment_basis_midijob(gross_wage, f)

    # Rates
    kv_total_rate = RATE_KV_BASE + additional_kv_rate
    an_kv_rate = kv_total_rate / 2.0
    ag_kv_rate = kv_total_rate / 2.0

    an_rv_rate = RATE_RV / 2.0
    ag_rv_rate = RATE_RV / 2.0

    an_av_rate = RATE_AV / 2.0
    ag_av_rate = RATE_AV / 2.0

    # PV with child relief / childless surcharge
    ag_pv_rate = 0.020
    an_pv_rate = 0.020
    if not has_children:
        an_pv_rate += RATE_PV_CHILDLESS  # 2.6%
    elif child_count > 1:
        # PUEG relief of 0.25% per child from 2nd to 5th child (max 1.0% relief)
        relief = min(0.010, (child_count - 1) * 0.0025)
        an_pv_rate = max(0.010, an_pv_rate - relief)

    # Employee contributions are based on reduced assessment basis B
    an_kv = round(b * an_kv_rate, 2)
    an_rv = round(b * an_rv_rate, 2)
    an_av = round(b * an_av_rate, 2)
    an_pv = round(b * an_pv_rate, 2)

    # Employer contributions are based on the actual gross wage E (§ 20 SGB IV)
    ag_kv = round(gross_wage * ag_kv_rate, 2)
    ag_rv = round(gross_wage * ag_rv_rate, 2)
    ag_av = round(gross_wage * ag_av_rate, 2)
    ag_pv = round(gross_wage * ag_pv_rate, 2)

    return (an_kv, an_rv, an_av, an_pv, ag_kv, ag_rv, ag_av, ag_pv)
