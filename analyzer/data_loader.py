# -*- coding: utf-8 -*-
"""
Blood Test Analyzer — File I/O
--------------------------------
This module is the only place that touches patients.csv and the
report file. It knows nothing about clinical logic (no BMI/BP-style
math here) — its only job is turning file rows into Python
dictionaries, and turning dictionaries back into file rows.

Created on Thu Jul 23 2026
@author: Amirhesam Karbakhsh
"""
import csv


def parse_value(raw_value):
    """
    Convert one raw CSV field into a usable test value.

    Three possible meanings for a field, and three different
    return values so downstream code can tell them apart:

    - ""            -> None       (test was not performed)
    - "13.5"        -> 13.5       (a normal, valid measurement)
    - "abc" / "N/A" -> "invalid"  (someone put non-numeric data
                                    in a numeric field — this is a
                                    DIFFERENT situation from "not
                                    tested" and should be reported
                                    as such, not silently treated
                                    the same way)

    Returns
    -------
    float, None, or the string "invalid"
    """
    if raw_value == "":
        return None

    try:
        value = float(raw_value)

    except ValueError:
        print(f"⚠️  '{raw_value}' is not a valid number — flagging as invalid data.")
        return "invalid"

    else:
        return value

    finally:
        print(f"Finished parsing value: '{raw_value}'")


def load_patients(filepath):
    """
    Read patients.csv and return a list of patient dictionaries.

    Each patient dict looks like:
        {"name": "Ali", "gender": "Male",
         "tests": {"hemoglobin": 13.0, "glucose": None, ...}}

    Returns
    -------
    list of dict
        Empty list if the file is missing or malformed — callers
        should treat an empty list as "nothing to report", not
        assume it means "no patients exist yet" without checking.
    """
    test_names = ["hemoglobin", "glucose", "cholesterol", "creatinine"]
    patients = []

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                tests = {}
                for test_name in test_names:
                    tests[test_name] = parse_value(row[test_name])

                patient = {
                    "name": row["name"],
                    "gender": row["gender"],
                    "tests": tests
                }
                patients.append(patient)

    except FileNotFoundError:
        print(f"⚠️  File not found: {filepath}")
        print("    No patients have been registered yet, or the file was moved.")
        return []

    except KeyError as missing_column:
        # This means the CSV header itself is missing an expected
        # column (name, gender, or one of the four test columns) —
        # the file's structure is broken, not just one row's data.
        print(f"⚠️  Missing expected column in CSV: {missing_column}")
        print("    Check that the header row matches: "
              "name,gender,hemoglobin,glucose,cholesterol,creatinine")
        return []

    else:
        return patients


def save_report(filepath, report):
    """
    Write the full report (list of dicts from build_report) to a
    CSV file, overwriting any previous report — the report always
    reflects the CURRENT state of all patients, not an accumulation
    of past runs.
    """
    try:
        fieldnames = report[0].keys()

    except IndexError:
        print("⚠️  Report is empty — nothing to save.")
        return

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(report)

    except PermissionError:
        print(f"⚠️  Cannot write to {filepath} — check if it's open in another program (like Excel).")

    else:
        print(f"✔ Report saved to {filepath}")


def ensure_csv_has_header(filepath, fieldnames):
    """
    Make sure patients.csv exists and starts with a header row.

    This matters because append_patient() always opens the file in
    "append" mode and only ever writes a data row — if the file
    didn't already have a header, the first patient's own data
    would be mistaken for the header the next time the file is
    read, silently corrupting every patient's data.

    Safe to call every time the program starts: if the file already
    exists, it is left completely untouched.
    """
    import os
    if not os.path.exists(filepath):
        with open(filepath, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()


def append_patient(filepath, patient_row):
    """
    Add one new patient (as a flat dict of strings, matching the
    CSV columns) to the end of patients.csv, without touching any
    existing rows.
    """
    try:
        with open(filepath, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=patient_row.keys())
            writer.writerow(patient_row)

    except PermissionError:
        print(f"⚠️  Cannot write to {filepath} — make sure it's not open in another program (like Excel).")

    except KeyError:
        print("⚠️  Patient data is missing the 'name' field.")

    else:
        print(f"✔ Patient '{patient_row.get('name', 'Unknown')}' added successfully.")
