# -*- coding: utf-8 -*-
"""
Blood Test Analyzer — Main Program
-------------------------------------
Console CLI that ties the analyzer package together:
register patients + their blood test results, then generate a
full clinical report from everything on file.

Created on Sun Jul 26 2026
@author: Amirhesam Karbakhsh
"""
import os

from analyzer.blood_analyzer import load_ranges, build_report
from analyzer.data_loader import (
    load_patients,
    save_report,
    append_patient,
    ensure_csv_has_header,
)


def clear_screen():
    """Clear the terminal screen based on the user's Operating System."""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_valid_gender(prompt="Gender (Male/Female): "):
    """
    Ask the user for gender and keep asking until it's exactly
    'Male' or 'Female' (case-insensitive on entry).
    """
    while True:
        raw_value = input(prompt).strip().capitalize()
        if raw_value in ("Male", "Female"):
            return raw_value
        print("⚠️  Please enter exactly 'Male' or 'Female'.")


def get_test_value(test_name):
    """
    Ask the user for one test's value. Loops until the entry is
    either empty (test skipped) or a valid number.

    Returns the RAW STRING (not a float) — CSV storage only needs
    text, and converting to a number happens later, once, when the
    file is actually read back (parse_value in data_loader.py).
    Converting here too would just be duplicated, wasted work.
    """
    while True:
        raw_value = input(f"  {test_name} (leave empty if not tested): ").strip()

        if raw_value == "":
            return ""

        try:
            float(raw_value)  # only checking validity, not keeping the result

        except ValueError:
            print(f"  ⚠️  '{raw_value}' is not a valid number. Try again.")
            continue

        else:
            return raw_value


def get_blood_test_input():
    """
    Prompt the user for a patient's name, gender, and the four
    supported blood test values.

    Returns
    -------
    dict
        A flat dictionary (no nested "tests" key) ready to be
        passed straight to append_patient(), since that's exactly
        the shape a CSV row needs.
    """
    test_names = ["hemoglobin", "glucose", "cholesterol", "creatinine"]

    name = input("Patient's name: ").strip()
    gender = get_valid_gender()
    patient_row = {"name": name, "gender": gender}

    for test_name in test_names:
        patient_row[test_name] = get_test_value(test_name)

    return patient_row


def show_author_info():
    """Display the developer profile inside a styled ASCII frame."""
    print("\n" + "┌" + "─" * 43 + "┐")
    print("│             DEVELOPER PROFILE               │")
    print("├" + "─" * 43 + "┤")
    print("│  👤 Author: Amirhesam Karbakhsh             │")
    print("│  🎓 Field: Biomedical Engineering           │")
    print("│  💻 GitHub: github.com/Hesamkb85            │")
    print("└" + "─" * 43 + "┘")


def display_menu():
    """Render the interactive console CLI main menu options."""
    print("\n" + "=" * 50)
    print("   🩸  BLOOD TEST ANALYZER  🩸")
    print("=" * 50)
    print(" [1] ➕ Register New Patient & Test Results")
    print(" [2] 📋 Generate & Save Full Report")
    print(" [3] 👤 Author Info")
    print(" [4] ❌ Exit")
    print("=" * 50)


# =============================================================================
# MAIN PROGRAM LOOP
# =============================================================================
patients_csv = "patients.csv"
ranges_file = os.path.join("analyzer", "ranges.json")
report_file = "blood_report.csv"
fieldnames = ["name", "gender", "hemoglobin", "glucose", "cholesterol", "creatinine"]

# Runs once at startup. If patients.csv doesn't exist yet, this creates
# it with just a header row, so the very first append_patient() call
# doesn't end up writing patient data as if it were the header.
ensure_csv_has_header(patients_csv, fieldnames)

if __name__ == "__main__":
    while True:
        clear_screen()
        display_menu()
        menu_input = input("Please select an option (1-4): ").strip()

        if menu_input == "1":
            # Loop so the user can register several patients back-to-back
            # without having to re-open the menu each time.
            while True:
                clear_screen()
                print("\n" + "-" * 35)
                print("     REGISTER NEW PATIENT & TESTS")
                print("-" * 35)

                patient_row = get_blood_test_input()
                append_patient(patients_csv, patient_row)

                another = input("\nAdd another patient? (y/n): ").strip().lower()
                if another != "y":
                    break

        elif menu_input == "2":
            clear_screen()

            ranges = load_ranges(ranges_file)
            if ranges is None:
                # load_ranges() already explained exactly what went
                # wrong (missing file / bad JSON) — nothing more to add.
                input("\nPress Enter to return to main menu...")
                continue

            patients = load_patients(patients_csv)
            if not patients:
                print("⚠️  No patients found to generate a report.")
                print("    Register at least one patient first (option 1).")
                input("\nPress Enter to return to main menu...")
                continue

            report = build_report(patients, ranges)
            save_report(report_file, report)

            input("\nPress Enter to return to main menu...")

        elif menu_input == "3":
            clear_screen()
            show_author_info()
            input("\nPress Enter to return to main menu...")

        elif menu_input == "4":
            clear_screen()
            print("\n" + "=" * 50)
            print("  Thank you for using Blood Test Analyzer! 👋")
            print("              Exiting program...")
            print("=" * 50)
            break

        else:
            print("\n❌ Invalid choice! Please select 1, 2, 3, or 4.")
            input("\nPress Enter to try again...")
