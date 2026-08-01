# -*- coding: utf-8 -*-
"""
Blood Test Analyzer — Core Clinical Logic
------------------------------------------
This module is the "brain" of the project: it knows how to load
reference ranges and how to classify a single test result as
low / normal / high. It does NOT talk to the user (no input/print
for interaction) and does not know anything about CSV files —
that separation is what keeps it easy to test and reuse.

Created on Thu Jul 23 2026
@author: Amirhesam Karbakhsh
"""
import json


def load_ranges(filepath):
    """
    Load the reference-range dictionary from a JSON file.

    Parameters
    ----------
    filepath : str
        Path to the ranges JSON file (e.g. "analyzer/ranges.json").

    Returns
    -------
    dict or None
        The parsed reference ranges on success.
        None if the file is missing or not valid JSON — callers
        MUST check for None before using the result, since the
        rest of the program cannot run without valid ranges.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            ranges = json.load(file)

    except FileNotFoundError:
        # This is not optional data — without it nothing else can
        # run, so we tell the user exactly what's missing and where.
        print(f"⚠️  Reference ranges file not found: '{filepath}'.")
        print("    Make sure 'ranges.json' exists inside the 'analyzer' folder.")
        return None

    except json.JSONDecodeError as error:
        # The file exists but its contents aren't valid JSON
        # (e.g. someone hand-edited it and broke the syntax).
        print(f"⚠️  '{filepath}' is not valid JSON ({error}).")
        print("    Check for a missing comma, bracket, or quote.")
        return None

    else:
        return ranges

    finally:
        # Runs no matter what — useful as a lightweight trace of
        # every attempt to load the ranges file, success or not.
        print(f"Finished attempting to load: {filepath}")


def analyze_test(test_name, value, ranges, gender=None):
    """
    Classify a single blood test value as 'low', 'normal', or 'high'.

    Parameters
    ----------
    test_name : str
        Key into `ranges`, e.g. "hemoglobin".
    value : float
        The measured value for this test.
    ranges : dict
        Reference ranges, as returned by load_ranges().
    gender : str, optional
        "male" or "female" — only used for tests whose normal
        range differs by gender (e.g. hemoglobin, creatinine).
        Comparison is case-insensitive, since the rest of the
        program stores gender as "Male"/"Female".

    Returns
    -------
    str
        "low", "normal", "high", or an explanatory message if the
        test isn't in the reference ranges at all.
    """
    # Normalize gender to lowercase because ranges.json uses
    # lowercase keys ("male"/"female") while the CLI stores
    # "Male"/"Female". Without this, gender-specific ranges would
    # NEVER match and every hemoglobin/creatinine check would
    # silently fall through to a missing "normal" key.
    if gender is not None:
        gender = gender.lower()

    try:
        test_ranges = ranges[test_name]

        if gender is not None and gender in test_ranges:
            low, high = test_ranges[gender]
        else:
            low, high = test_ranges["normal"]

    except KeyError:
        # Either the test itself isn't in ranges.json, or it IS
        # there but has no gender-neutral "normal" key and no
        # matching gender key either.
        return f"{test_name} not found in reference ranges."

    else:
        if value < low:
            status = "low"
        elif value <= high:
            status = "normal"
        else:
            status = "high"
        return status

    finally:
        print(f"Finished checking {test_name}.")


def build_report(patients, ranges):
    """
    Build a full report: one summary dict per patient, with a
    low/normal/high/not-tested status for each of the four tests.

    Parameters
    ----------
    patients : list of dict
        Each patient dict must have "name", "gender", and "tests"
        (a dict of test_name -> value, None, or "invalid").
    ranges : dict
        Reference ranges, as returned by load_ranges().

    Returns
    -------
    list of dict
        One row per patient. A patient record that is missing an
        expected field is SKIPPED (with a warning) instead of
        aborting the whole report — one bad record shouldn't cost
        you every other patient's results.
    """
    test_names = ["hemoglobin", "glucose", "cholesterol", "creatinine"]
    report = []

    for patient in patients:
        try:
            patient_report = {"name": patient["name"]}

            for test_name in test_names:
                value = patient["tests"][test_name]

                if value is None:
                    # Test wasn't performed for this patient.
                    patient_report[test_name] = "not tested"
                elif value == "invalid":
                    # Test WAS recorded, but the value in the CSV
                    # couldn't be parsed as a number (e.g. "abc").
                    # This is deliberately reported differently from
                    # "not tested" — it flags a data-quality problem
                    # instead of silently hiding it.
                    patient_report[test_name] = "invalid data"
                else:
                    status = analyze_test(test_name, value, ranges, patient.get("gender"))
                    patient_report[test_name] = status

        except KeyError as missing_field:
            print(f"⚠️  Skipping a patient record — missing field: {missing_field}")
            continue

        report.append(patient_report)

    return report
