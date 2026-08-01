# 🩸 Blood Test Analyzer

A console-based Python application for registering patients and
automatically classifying their blood test results (hemoglobin,
glucose, cholesterol, creatinine) against clinical reference ranges.

---

## Key Features

- **Patient registration** with input validation (name, gender, and
  four blood test values — any test can be left blank if not
  performed).
- **Reference-range-driven analysis**: normal ranges live in
  `analyzer/ranges.json`, not hardcoded in the logic — adding a new
  test or updating a range never requires touching the code.
- **Gender-aware ranges**: hemoglobin and creatinine use different
  normal ranges for male/female patients.
- **Honest error handling**: the program distinguishes between a
  test that was *not performed* ("not tested") and a test whose
  recorded value is *unreadable* ("invalid data") — instead of
  silently treating both the same way.
- **Resilient reporting**: a single corrupted patient record is
  skipped (with a warning) instead of crashing the whole report.

---

## Project Structure

```text
Blood_Test_Analyzer/
├── analyzer/
│   ├── __init__.py         # Marks this folder as a Python package
│   ├── ranges.json         # Reference ranges (edit this to add tests)
│   ├── blood_analyzer.py   # Clinical logic: load_ranges, analyze_test, build_report
│   └── data_loader.py      # File I/O: parse_value, load_patients, save_report, append_patient
├── main.py                 # CLI entry point / menu
├── patients.csv             # Patient database (auto-created on first run)
├── blood_report.csv         # Generated report (created by menu option 2)
└── README.md
```

## How to Run

```bash
python main.py
```

## Menu Options

1. **Register New Patient & Test Results** — enter a patient's name,
   gender, and any of the four blood test values (leave a value
   empty if that test wasn't performed). You can register several
   patients in a row before returning to the menu.
2. **Generate & Save Full Report** — reads every registered patient,
   classifies each test result, and writes `blood_report.csv`.
3. **Author Info**
4. **Exit**

## Reference Ranges

`analyzer/ranges.json` holds the normal range for each test:

```json
{
  "hemoglobin": {"male": [13.5, 17.5], "female": [12.0, 15.5]},
  "glucose": {"normal": [70, 99]},
  "cholesterol": {"normal": [125, 200]},
  "creatinine": {"male": [0.7, 1.3], "female": [0.6, 1.1]}
}
```

To add a new test (e.g. `"wbc"`), just add a new entry here — no
code changes required, as long as the test also gets added to the
`test_names` list in `blood_analyzer.py` and `data_loader.py`.

---

**Author:** Amirhesam Karbakhsh
**Field:** Biomedical Engineering
**GitHub:** github.com/Hesamkb85
