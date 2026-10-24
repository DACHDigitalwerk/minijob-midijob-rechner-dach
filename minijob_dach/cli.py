# -*- coding: utf-8 -*-
"""
Command-line interface for the DACH Minijob- & Midijob-Rechner 2026 (dach-midijob).
"""

import argparse
import json
import os
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from minijob_dach.models import Country, EmployerType, RVStatus
from minijob_dach.calculator import calculate_minijob_midijob


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dach-midijob",
        description="DACH Minijob-, Midijob- & Übergangsbereich-Rechner 2026 (556-€-Grenze, § 20 SGB IV)",
    )
    parser.add_argument(
        "--wage",
        "-w",
        type=float,
        default=556.0,
        help="Monatliches Bruttoarbeitsentgelt in EUR / CHF (Standard: 556.00)",
    )
    parser.add_argument(
        "--employer-type",
        "-e",
        type=str,
        choices=["commercial", "household"],
        default="commercial",
        help="Arbeitgeberart: 'commercial' (Gewerbe, 31.4%%) oder 'household' (Haushaltsscheck, 14.9%%)",
    )
    parser.add_argument(
        "--rv-exempt",
        action="store_true",
        help="Befreiung von der Rentenversicherungspflicht im Minijob beantragen (0%% Eigenanteil)",
    )
    parser.add_argument(
        "--country",
        "-c",
        type=str,
        choices=["DE", "AT", "CH"],
        default="DE",
        help="Länderregime: DE (556 € / SGB IV), AT (ASVG 551 €), CH (AHVV 2.300 CHF)",
    )
    parser.add_argument(
        "--tax-class",
        "-t",
        type=int,
        default=1,
        help="Steuerklasse (1-6, Standard: 1)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Ausgabe im strukturierten JSON-Format",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    emp_type = EmployerType.COMMERCIAL if args.employer_type == "commercial" else EmployerType.HOUSEHOLD
    rv_status = RVStatus.EXEMPTED if args.rv_exempt else RVStatus.MANDATORY
    country = Country(args.country.upper())

    res = calculate_minijob_midijob(
        gross_wage=args.wage,
        country=country,
        employer_type=emp_type,
        rv_status=rv_status,
        tax_class=args.tax_class,
    )

    if args.json:
        out = {
            "gross_wage": res.gross_wage,
            "country": res.country.value,
            "employment_type": res.employment_type.value,
            "employer_type": res.employer_type.value,
            "rv_status": res.rv_status.value,
            "assessment_basis_employee": res.assessment_basis_employee,
            "employee": {
                "kv": res.employee.kv,
                "rv": res.employee.rv,
                "av": res.employee.av,
                "pv": res.employee.pv,
                "wage_tax": res.employee.wage_tax,
                "total_social_security": res.employee.total_social_security,
                "total_deductions": res.employee.total_deductions,
                "net_wage": res.employee.net_wage,
            },
            "employer": {
                "kv": res.employer.kv,
                "rv": res.employer.rv,
                "av": res.employer.av,
                "pv": res.employer.pv,
                "flat_tax": res.employer.flat_tax,
                "u1": res.employer.u1,
                "u2": res.employer.u2,
                "insolvency_levy": res.employer.insolvency_levy,
                "accident_insurance": res.employer.accident_insurance,
                "total_levies": res.employer.total_levies_and_taxes,
                "total_costs": res.employer.total_employer_costs,
            },
            "full_pension_entitlement": res.full_pension_entitlement,
            "tax_advantage_household": res.tax_advantage_household_eur,
            "legal_notes": res.legal_notes,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    print("=" * 70)
    print(f" DACH MINIJOB- & MIDIJOB-ABRECHNUNG 2026 ({res.country.value})")
    print("=" * 70)
    print(f" Bruttolohn:               {res.gross_wage:>10.2f} € / CHF")
    print(f" Beschäftigungsstatus:     {res.employment_type.value}")
    print(f" Arbeitgeber-Modus:        {res.employer_type.value}")
    print(f" Fiktive Bemessungsgrundlage: {res.assessment_basis_employee:>7.2f} €")
    print("-" * 70)

    print("\n1. ARBEITNEHMER (ABZÜGE & NETTO):")
    print(f"  * Krankenversicherung (KV):      -{res.employee.kv:>8.2f} €")
    print(f"  * Rentenversicherung (RV):       -{res.employee.rv:>8.2f} €")
    print(f"  * Arbeitslosenvers. (AV):        -{res.employee.av:>8.2f} €")
    print(f"  * Pflegeversicherung (PV):       -{res.employee.pv:>8.2f} €")
    print(f"  * Lohnsteuer:                    -{res.employee.wage_tax:>8.2f} €")
    print(f"  * Gesamte AN-Abzüge:             -{res.employee.total_deductions:>8.2f} €")
    print(f"  -----------------------------------------------")
    print(f"  >> AUSZAHLUNGSBETRAG (NETTO):     {res.employee.net_wage:>8.2f} €")

    print("\n2. ARBEITGEBER (PAUSCHALABGABEN & GESAMTKOSTEN):")
    print(f"  * KV-Pauschale / Beitrag:         {res.employer.kv:>8.2f} €")
    print(f"  * RV-Pauschale / Beitrag:         {res.employer.rv:>8.2f} €")
    print(f"  * Pauschsteuer (2 %):             {res.employer.flat_tax:>8.2f} €")
    print(f"  * Umlagen U1/U2 & Inso:           {res.employer.u1 + res.employer.u2 + res.employer.insolvency_levy:>8.2f} €")
    print(f"  * Unfallversicherung (BG/UV):     {res.employer.accident_insurance:>8.2f} €")
    print(f"  * Summe Lohnnebenkosten:         +{res.employer.total_levies_and_taxes:>8.2f} €")
    print(f"  -----------------------------------------------")
    print(f"  >> GESAMTBELASTUNG ARBEITGEBER:   {res.employer.total_employer_costs:>8.2f} €")

    if res.tax_advantage_household_eur > 0:
        print(f"\n💡 Haushaltsscheck-Steuerbonus (§ 35a EStG): -{res.tax_advantage_household_eur:.2f} € / Monat!")

    print("\nRechtliche Hinweise:")
    for n in res.legal_notes:
        print(f"  • {n}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
