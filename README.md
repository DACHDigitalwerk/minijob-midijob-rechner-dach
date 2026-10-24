# 💼 DACH Minijob-, Midijob- & Übergangsbereich-Rechner 2026

[![CI](https://github.com/DACHDigitalwerk/minijob-midijob-rechner-dach/actions/workflows/ci.yml/badge.svg)](https://github.com/DACHDigitalwerk/minijob-midijob-rechner-dach/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Hochpräzise, modulare Python-Bibliothek und CLI-Tool zur gesetzeskonformen Berechnung von **Minijob (556-€-Grenze), Midijob / Übergangsbereich (556,01 € bis 2.000 € gem. § 20 SGB IV) und geringfügiger Beschäftigung 2026** für Deutschland, Österreich und die Schweiz.

🌐 **Interaktives Web-Tool & Schieberegler-Simulator:**  
Besuchen Sie unser kostenloses, 100 % clientseitiges Web-Tool:  
👉 **[DACH Minijob- & Midijob-Rechner 2026](https://dachdigitalwerk.github.io/minijob-midijob-rechner/)**

---

## 🚀 Kernfunktionen

### 1. 🇩🇪 Deutschland (SGB IV / SGB VI / SGB V)
- **Minijob-Grenze 2026:** Exakt **556,00 €** (gekoppelt an den Mindestlohn von 12,82 € x 130 : 3).
- **Gewerblicher Minijob:**
  - Arbeitgeber-Pauschalen: 15 % RV, 13 % KV, 2 % Pauschalsteuer, 1,4 % Umlagen (U1, U2, Insolvenzgeld).
  - Arbeitnehmer: 3,6 % Rentenversicherungsanteil (Differenz zu 18,6 % Regelbeitrag).
  - Befreiungsmöglichkeit nach § 6 Abs. 1b SGB VI.
- **Privathaushalt (Haushaltsscheck-Verfahren):**
  - AG-Abgaben nur 5 % RV + 5 % KV + 2 % Steuer + Umlagen & UV.
  - Steuerermäßigung nach § 35a EStG (20 %, max. 510 € / Jahr).
- **Midijob / Übergangsbereich (§ 20 SGB IV):**
  - Gleitzone von 556,01 € bis 2.000,00 €.
  - Exakter Faktor F (2026) zur Berechnung der fiktiven Bemessungsgrundlage.
  - Gleitender Anstieg der AN-Belastung von ca. 0 % bis zum vollen paritätischen Satz bei 2.000 €.
  - **Voller Rentenanspruch:** Volle Entgeltpunkte trotz reduzierter Beitragszahlung (§ 70 Abs. 1a SGB VI).

### 2. 🇦🇹 Österreich (ASVG)
- **Geringfügigkeitsgrenze 2026:** ~518,44 € monatlich.
- Nur Unfallversicherung (1,1 % AG-Beitrag), keine KV/PV/AV für den Arbeitnehmer.
- Option zur freiwilligen Selbstversicherung nach § 19a ASVG.
- Dienstgeberabgabe (DAG 16,4 %) bei mehreren geringfügig Beschäftigten.

### 3. 🇨🇭 Schweiz (AHVG / BVG)
- **Geringfügiger Lohn:** Bis 2.300 CHF pro Jahr beitragsfrei gem. Art. 8bis AHVV.
- **BVG-Eintrittsschwelle (2. Säule):** 22.050 CHF / Jahr (1.837,50 CHF / Monat).

---

## 📦 Installation

```bash
pip install git+https://github.com/DACHDigitalwerk/minijob-midijob-rechner-dach.git
```

---

## 💻 Verwendung

### CLI

```bash
# Minijob 556 EUR mit RV-Befreiung
dach-midijob --wage 556 --rv-exempt

# Midijob 1.200 EUR (Steuerklasse 1)
dach-midijob --wage 1200 --tax-class 1

# Österreich geringfügige Beschäftigung
dach-midijob --country AT --wage 500

# Schweiz geringfügiger Lohn
dach-midijob --country CH --wage 1500
```

JSON-Ausgabe:
```bash
dach-midijob --wage 1200 --json
```

---

## 🧪 Tests

```bash
pytest -v
```

---

## ⚖️ Rechtlicher Hinweis
Dieses Open-Source-Werkzeug dient der technischen Berechnung und Orientierung. Es stellt keine Rechts- oder Steuerberatung im Sinne des § 2 RDG bzw. § 5 StBerG dar.

---

## 📄 Lizenz
MIT License. Siehe [LICENSE](LICENSE) für Details.
