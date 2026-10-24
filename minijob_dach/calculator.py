# -*- coding: utf-8 -*-
"""
Main calculation engine for Minijob, Midijob, and Transitional Zone (Übergangsbereich) 2026.
Supports Germany, Austria (ASVG), and Switzerland (AHVV).
"""

from typing import List, Optional
from .models import (
    Country,
    EmploymentType,
    EmployerType,
    RVStatus,
    EmployeeDeductions,
    EmployerCosts,
    MidijobCalculationResult,
)
from .gleitzone import (
    LOWER_LIMIT_2026,
    UPPER_LIMIT_2026,
    compute_factor_f,
    compute_assessment_basis_midijob,
    calculate_midijob_social_security,
)


def calculate_minijob_midijob(
    gross_wage: float,
    country: Country = Country.DE,
    employer_type: EmployerType = EmployerType.COMMERCIAL,
    rv_status: RVStatus = RVStatus.EXEMPTED,
    tax_class: int = 1,
    has_children: bool = True,
    child_count: int = 1,
    additional_kv_rate: float = 0.017,
) -> MidijobCalculationResult:
    """
    Computes exact net wage, employee social security, employer costs, and tax benefits.
    """
    gross = round(max(0.0, gross_wage), 2)
    notes: List[str] = []

    if country == Country.DE:
        if gross <= LOWER_LIMIT_2026:
            # --- MINIJOB DEUTSCHLAND (bis 556,00 €) ---
            emp_type = EmploymentType.MINIJOB

            if employer_type == EmployerType.COMMERCIAL:
                # Gewerblicher Minijob
                # Arbeitnehmer
                if rv_status == RVStatus.MANDATORY:
                    an_rv = round(gross * 0.036, 2)  # 18.6% - 15.0% AG = 3.6% Eigenanteil
                    notes.append("Rentenversicherungspflicht: 3,6 % Eigenanteil für volle Rentenpunkte.")
                else:
                    an_rv = 0.0
                    notes.append("Befreiung von der RV-Pflicht gem. § 6 Abs. 1b SGB VI beantragt: 0 % Abzüge.")

                an_kv = 0.0
                an_av = 0.0
                an_pv = 0.0
                wage_tax = 0.0

                # Arbeitgeber (Pauschalsätze Minijob-Zentrale 2026)
                ag_kv = round(gross * 0.150, 2)            # 15.0% KV Pauschale
                ag_rv = round(gross * 0.150, 2)            # 15.0% RV Pauschale
                flat_tax = round(gross * 0.020, 2)         # 2.0% einheitliche Pauschsteuer
                u1 = round(gross * 0.007, 2)               # 0.7% Umlage U1 (Krankheit)
                u2 = round(gross * 0.0019, 2)              # 0.19% Umlage U2 (Mutterschutz)
                inso = round(gross * 0.0006, 2)            # 0.06% Insolvenzgeldumlage
                uv = round(gross * 0.016, 2)               # 1.6% gesetzliche Unfallversicherung (BG)

                tax_advantage_hh = 0.0

            else:
                # Privathaushalt (Haushaltsscheckverfahren)
                if rv_status == RVStatus.MANDATORY:
                    an_rv = round(gross * 0.136, 2)  # 18.6% - 5.0% AG = 13.6%
                    notes.append("Haushalt: Volle RV-Versicherungspflicht mit 13,6 % Eigenanteil.")
                else:
                    an_rv = 0.0
                    notes.append("Haushaltsscheck: RV-Befreiung aktiv. Keine Abzüge für den Minijobber.")

                an_kv = 0.0
                an_av = 0.0
                an_pv = 0.0
                wage_tax = 0.0

                ag_kv = round(gross * 0.050, 2)            # 5.0% KV Pauschale
                ag_rv = round(gross * 0.050, 2)            # 5.0% RV Pauschale
                flat_tax = round(gross * 0.020, 2)         # 2.0% Pauschsteuer
                u1 = round(gross * 0.011, 2)               # 1.1% Umlage U1
                u2 = round(gross * 0.0019, 2)              # 0.19% Umlage U2
                inso = 0.0                                 # Keine Insolvenzumlage bei Haushalten
                uv = round(gross * 0.016, 2)               # 1.6% Unfallversicherung

                # § 35a EStG Steuerermäßigung für Privathaushalt: 20% der Gesamtaufwendungen, max 510 € p.a.
                total_ag_before_tax_break = gross + ag_kv + ag_rv + flat_tax + u1 + u2 + uv
                tax_advantage_hh = round(min(510.0 / 12.0, total_ag_before_tax_break * 0.20), 2)
                notes.append(f"Steuervorteil § 35a EStG für Privathaushalt: Bis zu {tax_advantage_hh:.2f} €/Monat direkte Steuerersparnis.")

            total_an_sv = an_kv + an_rv + an_av + an_pv
            total_an_ded = total_an_sv + wage_tax
            net_wage = round(gross - total_an_ded, 2)

            total_ag_levies = ag_kv + ag_rv + flat_tax + u1 + u2 + inso + uv
            total_ag_costs = round(gross + total_ag_levies, 2)
            assessment_basis = gross

            return MidijobCalculationResult(
                gross_wage=gross,
                country=country,
                employment_type=emp_type,
                employer_type=employer_type,
                rv_status=rv_status,
                assessment_basis_employee=assessment_basis,
                employee=EmployeeDeductions(
                    kv=an_kv,
                    rv=an_rv,
                    av=an_av,
                    pv=an_pv,
                    wage_tax=wage_tax,
                    church_tax=0.0,
                    solidarity_surcharge=0.0,
                    total_social_security=total_an_sv,
                    total_deductions=total_an_ded,
                    net_wage=net_wage,
                ),
                employer=EmployerCosts(
                    kv=ag_kv,
                    rv=ag_rv,
                    av=0.0,
                    pv=0.0,
                    flat_tax=flat_tax,
                    u1=u1,
                    u2=u2,
                    insolvency_levy=inso,
                    accident_insurance=uv,
                    total_levies_and_taxes=round(total_ag_levies, 2),
                    total_employer_costs=total_ag_costs,
                ),
                full_pension_entitlement=(rv_status == RVStatus.MANDATORY),
                tax_advantage_household_eur=tax_advantage_hh,
                legal_notes=notes,
            )

        elif gross <= UPPER_LIMIT_2026:
            # --- MIDIJOB / ÜBERGANGSBEREICH (556,01 € bis 2.000,00 €) ---
            emp_type = EmploymentType.MIDIJOB
            f = compute_factor_f(additional_kv_rate)
            b = compute_assessment_basis_midijob(gross, f)

            an_kv, an_rv, an_av, an_pv, ag_kv, ag_rv, ag_av, ag_pv = calculate_midijob_social_security(
                gross, additional_kv_rate, has_children, child_count
            )

            # Lohnsteuer im Übergangsbereich: Bei Steuerklasse 1 bis ca. 1.300 € steuerfrei
            if tax_class == 1:
                if gross > 1350.0:
                    wage_tax = round((gross - 1350.0) * 0.14, 2)
                else:
                    wage_tax = 0.0
            else:
                wage_tax = round(gross * 0.09, 2)

            u1 = round(gross * 0.007, 2)
            u2 = round(gross * 0.0019, 2)
            inso = round(gross * 0.0006, 2)
            uv = round(gross * 0.016, 2)

            total_an_sv = round(an_kv + an_rv + an_av + an_pv, 2)
            total_an_ded = round(total_an_sv + wage_tax, 2)
            net_wage = round(gross - total_an_ded, 2)

            total_ag_levies = round(ag_kv + ag_rv + ag_av + ag_pv + u1 + u2 + inso + uv, 2)
            total_ag_costs = round(gross + total_ag_levies, 2)

            notes.append(f"Gleitzonenformel § 20 SGB IV angewendet (Faktor F: {f:.4f}).")
            notes.append(f"Reduzierte fiktive Beitragsbemessungsgrundlage AN: {b:.2f} € (statt {gross:.2f} €).")
            notes.append("Voller Rentenanspruch gem. § 70 Abs. 1a SGB VI auf Basis des tatsächlichen Entgelts!")

            return MidijobCalculationResult(
                gross_wage=gross,
                country=country,
                employment_type=emp_type,
                employer_type=employer_type,
                rv_status=RVStatus.MANDATORY,
                assessment_basis_employee=b,
                employee=EmployeeDeductions(
                    kv=an_kv,
                    rv=an_rv,
                    av=an_av,
                    pv=an_pv,
                    wage_tax=wage_tax,
                    church_tax=0.0,
                    solidarity_surcharge=0.0,
                    total_social_security=total_an_sv,
                    total_deductions=total_an_ded,
                    net_wage=net_wage,
                ),
                employer=EmployerCosts(
                    kv=ag_kv,
                    rv=ag_rv,
                    av=ag_av,
                    pv=ag_pv,
                    flat_tax=0.0,
                    u1=u1,
                    u2=u2,
                    insolvency_levy=inso,
                    accident_insurance=uv,
                    total_levies_and_taxes=total_ag_levies,
                    total_employer_costs=total_ag_costs,
                ),
                full_pension_entitlement=True,
                tax_advantage_household_eur=0.0,
                legal_notes=notes,
            )

        else:
            # --- REGULÄRES ARBEITSVERHÄLTNIS (> 2.000,00 €) ---
            emp_type = EmploymentType.REGULAR
            an_kv = round(gross * ((0.146 + additional_kv_rate) / 2.0), 2)
            ag_kv = an_kv
            an_rv = round(gross * (0.186 / 2.0), 2)
            ag_rv = an_rv
            an_av = round(gross * (0.026 / 2.0), 2)
            ag_av = an_av
            an_pv = round(gross * (0.026 if not has_children else 0.020), 2)
            ag_pv = round(gross * 0.020, 2)

            wage_tax = round((gross - 1200.0) * 0.18, 2) if gross > 1200 else 0.0
            u1 = round(gross * 0.007, 2)
            u2 = round(gross * 0.0019, 2)
            inso = round(gross * 0.0006, 2)
            uv = round(gross * 0.016, 2)

            total_an_sv = round(an_kv + an_rv + an_av + an_pv, 2)
            total_an_ded = round(total_an_sv + wage_tax, 2)
            net_wage = round(gross - total_an_ded, 2)

            total_ag_levies = round(ag_kv + ag_rv + ag_av + ag_pv + u1 + u2 + inso + uv, 2)
            total_ag_costs = round(gross + total_ag_levies, 2)

            notes.append("Reguläre Vollbeschäftigung oberhalb des Übergangsbereichs (> 2.000 €).")

            return MidijobCalculationResult(
                gross_wage=gross,
                country=country,
                employment_type=emp_type,
                employer_type=employer_type,
                rv_status=RVStatus.MANDATORY,
                assessment_basis_employee=gross,
                employee=EmployeeDeductions(
                    kv=an_kv,
                    rv=an_rv,
                    av=an_av,
                    pv=an_pv,
                    wage_tax=wage_tax,
                    church_tax=0.0,
                    solidarity_surcharge=0.0,
                    total_social_security=total_an_sv,
                    total_deductions=total_an_ded,
                    net_wage=net_wage,
                ),
                employer=EmployerCosts(
                    kv=ag_kv,
                    rv=ag_rv,
                    av=ag_av,
                    pv=ag_pv,
                    flat_tax=0.0,
                    u1=u1,
                    u2=u2,
                    insolvency_levy=inso,
                    accident_insurance=uv,
                    total_levies_and_taxes=total_ag_levies,
                    total_employer_costs=total_ag_costs,
                ),
                full_pension_entitlement=True,
                tax_advantage_household_eur=0.0,
                legal_notes=notes,
            )

    elif country == Country.AT:
        # --- ÖSTERREICH (ASVG 2026) ---
        limit_at = 551.10  # Geringfügigkeitsgrenze ASVG 2026
        if gross <= limit_at:
            emp_type = EmploymentType.MINIJOB
            an_sv = 0.0
            ag_uv = round(gross * 0.011, 2)  # 1.1% Unfallversicherung
            notes.append(f"Geringfügig beschäftigt nach § 5 Abs. 2 ASVG (Grenze: {limit_at:.2f} €).")
            notes.append("Dienstnehmer ist beitragsfrei. Optionale Selbstversicherung gem. § 19a ASVG möglich.")
            return MidijobCalculationResult(
                gross_wage=gross,
                country=country,
                employment_type=emp_type,
                employer_type=employer_type,
                rv_status=RVStatus.EXEMPTED,
                assessment_basis_employee=gross,
                employee=EmployeeDeductions(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, gross),
                employer=EmployerCosts(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ag_uv, ag_uv, round(gross + ag_uv, 2)),
                full_pension_entitlement=False,
                tax_advantage_household_eur=0.0,
                legal_notes=notes,
            )
        else:
            emp_type = EmploymentType.REGULAR
            # Standard AT SV deductions: ca. 18.12% AN, 21.38% AG
            an_sv = round(gross * 0.1812, 2)
            ag_sv = round(gross * 0.2138, 2)
            net_wage = round(gross - an_sv, 2)
            notes.append("Vollversicherung nach ASVG (Kranken-, Pensions- und Unfallversicherung).")
            return MidijobCalculationResult(
                gross_wage=gross,
                country=country,
                employment_type=emp_type,
                employer_type=employer_type,
                rv_status=RVStatus.MANDATORY,
                assessment_basis_employee=gross,
                employee=EmployeeDeductions(round(gross*0.0387,2), round(gross*0.1025,2), round(gross*0.03,2), 0.0, 0.0, 0.0, 0.0, an_sv, an_sv, net_wage),
                employer=EmployerCosts(round(gross*0.0378,2), round(gross*0.1255,2), round(gross*0.03,2), 0.0, 0.0, 0.0, 0.0, 0.0, round(gross*0.011,2), ag_sv, round(gross + ag_sv, 2)),
                full_pension_entitlement=True,
                tax_advantage_household_eur=0.0,
                legal_notes=notes,
            )

    else:
        # --- SCHWEIZ (AHVV 2026) ---
        annual_limit_ch = 2300.0  # Art. 34d AHVV (ca. 191.60 CHF / Monat)
        monthly_limit_ch = round(annual_limit_ch / 12.0, 2)
        if gross <= monthly_limit_ch and employer_type != EmployerType.HOUSEHOLD:
            emp_type = EmploymentType.MINIJOB
            notes.append(f"Geringfügiger Lohn nach Art. 34d AHVV (unter {annual_limit_ch:.0f} CHF/Jahr): Beitragsfrei zur AHV/IV/EO/ALV.")
            return MidijobCalculationResult(
                gross_wage=gross,
                country=country,
                employment_type=emp_type,
                employer_type=employer_type,
                rv_status=RVStatus.EXEMPTED,
                assessment_basis_employee=gross,
                employee=EmployeeDeductions(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, gross),
                employer=EmployerCosts(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, gross),
                full_pension_entitlement=False,
                tax_advantage_household_eur=0.0,
                legal_notes=notes,
            )
        else:
            # Privathaushalt (BGSA 11.4%) oder über Grenze (AHV/IV/EO 5.3% + ALV 1.1% = 6.4% je AN und AG)
            emp_type = EmploymentType.REGULAR
            an_ahv = round(gross * 0.053, 2)
            an_alv = round(gross * 0.011, 2)
            total_an = an_ahv + an_alv
            total_ag = total_an
            notes.append("Beitragspflichtig zur 1. Säule (AHV/IV/EO und ALV).")
            return MidijobCalculationResult(
                gross_wage=gross,
                country=country,
                employment_type=emp_type,
                employer_type=employer_type,
                rv_status=RVStatus.MANDATORY,
                assessment_basis_employee=gross,
                employee=EmployeeDeductions(0.0, an_ahv, an_alv, 0.0, 0.0, 0.0, 0.0, total_an, total_an, round(gross - total_an, 2)),
                employer=EmployerCosts(0.0, an_ahv, an_alv, 0.0, 0.0, 0.0, 0.0, 0.0, round(gross * 0.015, 2), round(total_ag + gross * 0.015, 2), round(gross + total_ag + gross * 0.015, 2)),
                full_pension_entitlement=True,
                tax_advantage_household_eur=0.0,
                legal_notes=notes,
            )
