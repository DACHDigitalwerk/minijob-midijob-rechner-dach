# -*- coding: utf-8 -*-
"""
Quickstart Example: DACH Minijob-, Midijob- & Übergangsbereich-Rechner 2026.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from minijob_dach import (
    Country,
    EmployerType,
    RVStatus,
    calculate_minijob_midijob,
)


def main():
    print("=== Quickstart: Minijob & Midijob 2026 (DACH) ===")

    # 1. 556-€-Minijob mit Rentenversicherungspflicht (3,6 % Eigenanteil)
    print("\n--- Fall 1: Minijobber 556 € mit Rentenversicherungspflicht ---")
    res1 = calculate_minijob_midijob(
        gross_wage=556.00,
        country=Country.DE,
        employer_type=EmployerType.COMMERCIAL,
        rv_status=RVStatus.MANDATORY,
    )
    print(f"Bruttolohn:                {res1.gross_wage:.2f} €")
    print(f"AN-Rentenversicherung:    -{res1.employee.rv:.2f} € (3,6 % Eigenanteil)")
    print(f"Nettolohn:                 {res1.employee.net_wage:.2f} €")
    print(f"AG-Pauschalabgaben (31,4%):+{res1.employer.total_levies_and_taxes:.2f} €")
    print(f"AG-Gesamtkosten:           {res1.employer.total_employer_costs:.2f} €")
    print(f"Rentenpunkte-Status:       {'Voller Erwerb' if res1.full_pension_entitlement else 'Kein Erwerb'}")

    # 2. Midijob 1.200 € im Übergangsbereich (§ 20 SGB IV)
    print("\n--- Fall 2: Midijobber 1.200 € im Übergangsbereich (§ 20 SGB IV) ---")
    res2 = calculate_minijob_midijob(
        gross_wage=1200.00,
        country=Country.DE,
        tax_class=1,
    )
    print(f"Bruttolohn:                {res2.gross_wage:.2f} €")
    print(f"Fiktive Bemessungsgrundlage: {res2.assessment_basis_employee:.2f} € (gem. Gleitzonenformel)")
    print(f"Tatsächliche AN-Abzüge:   -{res2.employee.total_deductions:.2f} €")
    print(f"Nettolohn:                 {res2.employee.net_wage:.2f} €")
    print(f"AG-Lohnnebenkosten:       +{res2.employer.total_levies_and_taxes:.2f} €")
    print(f"AG-Gesamtkosten:           {res2.employer.total_employer_costs:.2f} €")
    print(f"Volle Rentenansprüche:     {'JA (§ 70 Abs. 1a SGB VI)' if res2.full_pension_entitlement else 'NEIN'}")


if __name__ == "__main__":
    main()
