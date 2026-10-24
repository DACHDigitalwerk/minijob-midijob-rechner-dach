# -*- coding: utf-8 -*-
"""
minijob_dach: DACH Minijob-, Midijob- & Übergangsbereich-Rechner 2026.
556-€-Grenze, Gleitzonenformel § 20 SGB IV, DE / AT / CH.
"""

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
from .calculator import calculate_minijob_midijob

__version__ = "1.0.0"
__all__ = [
    "Country",
    "EmploymentType",
    "EmployerType",
    "RVStatus",
    "EmployeeDeductions",
    "EmployerCosts",
    "MidijobCalculationResult",
    "LOWER_LIMIT_2026",
    "UPPER_LIMIT_2026",
    "compute_factor_f",
    "compute_assessment_basis_midijob",
    "calculate_midijob_social_security",
    "calculate_minijob_midijob",
    "__version__",
]
