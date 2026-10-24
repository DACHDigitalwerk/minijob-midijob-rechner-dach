# -*- coding: utf-8 -*-
"""
Data models for Minijob, Midijob, and Transitional Zone (Übergangsbereich) calculation 2026 (DE, AT, CH).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Country(str, Enum):
    DE = "DE"
    AT = "AT"
    CH = "CH"


class EmploymentType(str, Enum):
    MINIJOB = "MINIJOB"              # <= 556.00 € (DE) / geringfügig
    MIDIJOB = "MIDIJOB"              # 556.01 € - 2000.00 € (DE Übergangsbereich)
    REGULAR = "REGULAR"              # > 2000.00 €


class EmployerType(str, Enum):
    COMMERCIAL = "COMMERCIAL"        # Gewerblicher Betrieb (31,4 % Pauschalabgaben)
    HOUSEHOLD = "HOUSEHOLD"          # Privathaushalt / Haushaltsscheckverfahren (14,9 %)


class RVStatus(str, Enum):
    EXEMPTED = "EXEMPTED"            # Befreiung von der RV-Pflicht beantragt (0% AN-Beitrag)
    MANDATORY = "MANDATORY"          # Versicherungspflichtig in RV (3,6% AN-Eigenanteil)


@dataclass
class EmployeeDeductions:
    kv: float                        # Krankenversicherung
    rv: float                        # Rentenversicherung
    av: float                        # Arbeitslosenversicherung
    pv: float                        # Pflegeversicherung
    wage_tax: float                  # Lohnsteuer
    church_tax: float                # Kirchensteuer
    solidarity_surcharge: float      # Solidaritätszuschlag
    total_social_security: float
    total_deductions: float
    net_wage: float


@dataclass
class EmployerCosts:
    kv: float                        # KV-Pauschale / AG-Anteil
    rv: float                        # RV-Pauschale / AG-Anteil
    av: float                        # AV-Beitrag
    pv: float                        # PV-Beitrag
    flat_tax: float                  # Pauschsteuer (z.B. 2% Minijob)
    u1: float                        # Umlage U1 (Krankheit)
    u2: float                        # Umlage U2 (Mutterschutz)
    insolvency_levy: float           # Insolvenzgeldumlage
    accident_insurance: float        # Unfallversicherung (BG / UV)
    total_levies_and_taxes: float
    total_employer_costs: float     # Bruttolohn + AG-Nebenkosten


@dataclass
class MidijobCalculationResult:
    gross_wage: float
    country: Country
    employment_type: EmploymentType
    employer_type: EmployerType
    rv_status: RVStatus
    assessment_basis_employee: float  # Fiktive Bemessungsgrundlage gem. § 20 SGB IV
    employee: EmployeeDeductions
    employer: EmployerCosts
    full_pension_entitlement: bool   # Erwerb voller Rentenpunkte trotz reduzierter Beiträge
    tax_advantage_household_eur: float  # § 35a EStG 20% Steuerabzug bei Haushalten
    legal_notes: List[str] = field(default_factory=list)
