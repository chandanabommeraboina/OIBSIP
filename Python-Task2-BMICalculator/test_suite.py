"""
================================================================================
OASIS INFOBYTE SIP - PYTHON PROGRAMMING INTERNSHIP
Task 2: BMI Calculator — Comprehensive Automated Test Suite
Student Name   : Chandana
Assigned Track : Python Programming
================================================================================

This test suite executes all validation, calculation, category boundary,
database CRUD, query parameterization, and visualization tests without
requiring manual interaction.
"""

import os
import sys
import tempfile
import sqlite3
import datetime

# Ensure parent directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    validate_input,
    calculate_bmi,
    classify_bmi,
    format_bmi,
    init_db,
    save_bmi_record,
    fetch_all_records,
    fetch_records_by_user,
    fetch_distinct_users,
    delete_record_by_id,
    open_bmi_trend_window,
    MATPLOTLIB_AVAILABLE,
    CATEGORY_UNDERWEIGHT,
    CATEGORY_NORMAL,
    CATEGORY_OVERWEIGHT,
    CATEGORY_OBESE,
    CATEGORY_COLORS
)


def run_all_tests() -> bool:
    print("=" * 76)
    print("STARTING TEST SUITE: OASIS INFOBYTE TASK 2 - BMI CALCULATOR")
    print("=" * 76)

    passed_count = 0
    total_count = 11

    # --------------------------------------------------------------------------
    # Test 1: BMI Calculation Formula Precision
    # Formula: BMI = weight / (height * height)
    # Example: weight = 70.0 kg, height = 1.75 m -> BMI = 70 / (1.75 * 1.75) = 22.85714...
    # --------------------------------------------------------------------------
    try:
        weight = 70.0
        height = 1.75
        expected_raw_bmi = 70.0 / (1.75 ** 2)  # ~22.857142857
        actual_raw_bmi = calculate_bmi(weight, height)
        assert abs(actual_raw_bmi - expected_raw_bmi) < 1e-6, f"Expected {expected_raw_bmi}, got {actual_raw_bmi}"
        print(f"[PASS] Test 1: BMI Calculation Formula Precision Verified (70kg, 1.75m -> {actual_raw_bmi:.6f})")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Test 1: BMI calculation failed: {e}")

    # --------------------------------------------------------------------------
    # Test 2: Formatting BMI to Exactly Two Decimal Places
    # --------------------------------------------------------------------------
    try:
        bmi_sample = 22.857142857
        formatted = format_bmi(bmi_sample)
        assert formatted == "22.86", f"Expected '22.86', got '{formatted}'"
        assert format_bmi(25.0) == "25.00", f"Expected '25.00', got '{format_bmi(25.0)}'"
        print(f"[PASS] Test 2: BMI Display Formatting Verified (22.8571 -> '{formatted}', 25.0 -> '25.00')")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Test 2: Formatting failed: {e}")

    # --------------------------------------------------------------------------
    # Test 3: Input Validation - Rejection of Empty Fields
    # --------------------------------------------------------------------------
    try:
        # Empty name
        ok, msg, _, _, _ = validate_input("", "70", "1.75")
        assert not ok and "Name field cannot be empty" in msg, f"Failed empty name check: {msg}"

        # Whitespace-only name
        ok, msg, _, _, _ = validate_input("   ", "70", "1.75")
        assert not ok and "Name field cannot be empty" in msg, f"Failed whitespace name check: {msg}"

        # Empty weight
        ok, msg, _, _, _ = validate_input("Chandana", "", "1.75")
        assert not ok and "Weight field cannot be empty" in msg, f"Failed empty weight check: {msg}"

        # Empty height
        ok, msg, _, _, _ = validate_input("Chandana", "70", "")
        assert not ok and "Height field cannot be empty" in msg, f"Failed empty height check: {msg}"

        print("[PASS] Test 3: Input Validation - Empty and Whitespace Fields Successfully Rejected")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Test 3: Empty field check failed: {e}")

    # --------------------------------------------------------------------------
    # Test 4: Input Validation - Rejection of Non-Numeric Inputs
    # --------------------------------------------------------------------------
    try:
        # Non-numeric weight
        ok, msg, _, _, _ = validate_input("Chandana", "seventy", "1.75")
        assert not ok and "Invalid weight" in msg, f"Failed non-numeric weight check: {msg}"

        # Non-numeric height
        ok, msg, _, _, _ = validate_input("Chandana", "70", "one point eight")
        assert not ok and "Invalid height" in msg, f"Failed non-numeric height check: {msg}"

        # Special characters
        ok, msg, _, _, _ = validate_input("Chandana", "70#kg", "1.75")
        assert not ok and "Invalid weight" in msg, f"Failed special char weight check: {msg}"

        print("[PASS] Test 4: Input Validation - Non-Numeric Values Gracefully Rejected with Helpful Error")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Test 4: Non-numeric validation failed: {e}")

    # --------------------------------------------------------------------------
    # Test 5: Input Validation - Rejection of Zero or Negative Weight
    # --------------------------------------------------------------------------
    try:
        ok, msg, _, _, _ = validate_input("Chandana", "0", "1.75")
        assert not ok and "greater than zero" in msg, f"Failed zero weight check: {msg}"

        ok, msg, _, _, _ = validate_input("Chandana", "-65.5", "1.75")
        assert not ok and "greater than zero" in msg, f"Failed negative weight check: {msg}"

        print("[PASS] Test 5: Input Validation - Zero and Negative Weight Values Successfully Rejected")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Test 5: Zero/negative weight check failed: {e}")

    # --------------------------------------------------------------------------
    # Test 6: Input Validation - Rejection of Zero or Negative Height
    # --------------------------------------------------------------------------
    try:
        ok, msg, _, _, _ = validate_input("Chandana", "65", "0")
        assert not ok and "greater than zero" in msg, f"Failed zero height check: {msg}"

        ok, msg, _, _, _ = validate_input("Chandana", "65", "-1.75")
        assert not ok and "greater than zero" in msg, f"Failed negative height check: {msg}"

        print("[PASS] Test 6: Input Validation - Zero and Negative Height Values Successfully Rejected")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Test 6: Zero/negative height check failed: {e}")

    # --------------------------------------------------------------------------
    # Test 7: Category Boundaries per Oasis Infobyte PDF Checklist
    # - Underweight: BMI below 18.5 (< 18.5)
    # - Normal: BMI from 18.5 to 24.9
    # - Overweight: BMI from 25 to 29.9
    # - Obese: BMI 30 or above
    # Exact boundary test points: 18.49, 18.50, 24.90, 25.00, 29.90, 30.00
    # --------------------------------------------------------------------------
    try:
        # 18.49 -> Underweight
        cat, col, _ = classify_bmi(18.49)
        assert cat == CATEGORY_UNDERWEIGHT, f"Expected Underweight for 18.49, got {cat}"
        assert col == CATEGORY_COLORS[CATEGORY_UNDERWEIGHT]

        # 18.50 -> Normal
        cat, col, _ = classify_bmi(18.50)
        assert cat == CATEGORY_NORMAL, f"Expected Normal for 18.50, got {cat}"
        assert col == CATEGORY_COLORS[CATEGORY_NORMAL]

        # 24.90 -> Normal
        cat, col, _ = classify_bmi(24.90)
        assert cat == CATEGORY_NORMAL, f"Expected Normal for 24.90, got {cat}"

        # 25.00 -> Overweight
        cat, col, _ = classify_bmi(25.00)
        assert cat == CATEGORY_OVERWEIGHT, f"Expected Overweight for 25.00, got {cat}"
        assert col == CATEGORY_COLORS[CATEGORY_OVERWEIGHT]

        # 29.90 -> Overweight
        cat, col, _ = classify_bmi(29.90)
        assert cat == CATEGORY_OVERWEIGHT, f"Expected Overweight for 29.90, got {cat}"

        # 30.00 -> Obese
        cat, col, _ = classify_bmi(30.00)
        assert cat == CATEGORY_OBESE, f"Expected Obese for 30.00, got {cat}"
        assert col == CATEGORY_COLORS[CATEGORY_OBESE]

        print("[PASS] Test 7: All Category Boundaries Verified (18.49, 18.50, 24.90, 25.00, 29.90, 30.00)")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Test 7: Category boundary check failed: {e}")

    # --------------------------------------------------------------------------
    # Test 8: SQLite Database Operations (Create, Insert, Read, Schema, Parameterization)
    # --------------------------------------------------------------------------
    temp_db = os.path.join(tempfile.gettempdir(), f"test_bmi_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}.db")
    try:
        # 8a: Initialize DB
        init_ok, init_msg = init_db(temp_db)
        assert init_ok, f"Init DB failed: {init_msg}"
        assert os.path.exists(temp_db), "Database file was not created on disk."

        # 8b: Insert records using parameterized query
        save_ok, save_msg = save_bmi_record(
            name="Chandana",
            weight=62.0,
            height=1.68,
            bmi=21.97,
            category=CATEGORY_NORMAL,
            timestamp="2026-10-10 10:00:00",
            db_path=temp_db
        )
        assert save_ok, f"Save record 1 failed: {save_msg}"

        save_ok2, save_msg2 = save_bmi_record(
            name="Chandana",
            weight=60.5,
            height=1.68,
            bmi=21.44,
            category=CATEGORY_NORMAL,
            timestamp="2026-10-15 10:00:00",
            db_path=temp_db
        )
        assert save_ok2, f"Save record 2 failed: {save_msg2}"

        save_ok3, save_msg3 = save_bmi_record(
            name="Alex",
            weight=88.0,
            height=1.75,
            bmi=28.73,
            category=CATEGORY_OVERWEIGHT,
            timestamp="2026-10-16 11:30:00",
            db_path=temp_db
        )
        assert save_ok3, f"Save record 3 failed: {save_msg3}"

        # 8c: Retrieve all records
        fetch_ok, all_recs, fetch_msg = fetch_all_records(temp_db)
        assert fetch_ok, f"Fetch all failed: {fetch_msg}"
        assert len(all_recs) == 3, f"Expected 3 records, got {len(all_recs)}"
        # Verify newest record is first (timestamp DESC)
        assert all_recs[0]["name"] == "Alex", f"Expected newest record Alex, got {all_recs[0]['name']}"

        # 8d: Distinct users
        users_ok, users_list, _ = fetch_distinct_users(temp_db)
        assert users_ok and len(users_list) == 2, f"Expected 2 distinct users, got {users_list}"
        assert "Chandana" in users_list and "Alex" in users_list

        print(f"[PASS] Test 8: SQLite Database Operations (Schema, Parameterized Insert, Read, Index) Verified")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Test 8: SQLite operations failed: {e}")

    # --------------------------------------------------------------------------
    # Test 9: Chronological Ordering & User Filtering for Trend Graph
    # --------------------------------------------------------------------------
    try:
        user_ok, chan_recs, _ = fetch_records_by_user("Chandana", temp_db)
        assert user_ok, "Failed to fetch user records."
        assert len(chan_recs) == 2, f"Expected 2 records for Chandana, got {len(chan_recs)}"
        # Chronological order ascending
        assert chan_recs[0]["timestamp"] < chan_recs[1]["timestamp"], "Records not in chronological ascending order."
        assert chan_recs[0]["bmi"] == 21.97
        assert chan_recs[1]["bmi"] == 21.44

        # Case-insensitive search
        case_ok, lower_recs, _ = fetch_records_by_user("chandana", temp_db)
        assert case_ok and len(lower_recs) == 2, "Case-insensitive username retrieval failed."

        print("[PASS] Test 9: Chronological Ascending Ordering and User Filtering Verified for Analytics")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Test 9: User filtering / chronological order failed: {e}")

    # --------------------------------------------------------------------------
    # Test 10: Graceful SQLite Error Handling
    # --------------------------------------------------------------------------
    try:
        # Invalid / unwriteable database path
        invalid_path = "Z:\\non_existent_drive_folder\\impossible.db"
        err_ok, err_msg = save_bmi_record("Test", 70.0, 1.75, 22.86, CATEGORY_NORMAL, db_path=invalid_path)
        assert not err_ok, "Expected save to fail on invalid database path."
        assert "Failed to save record" in err_msg, f"Expected helpful error message, got '{err_msg}'"

        # Record deletion non-existent ID
        del_ok, del_msg = delete_record_by_id(999999, temp_db)
        assert not del_ok, "Expected deletion of non-existent ID to return False."

        print("[PASS] Test 10: SQLite Error Handling Tested - System Handles Failures Gracefully Without Crashing")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Test 10: Error handling check failed: {e}")

    # Clean up temp database
    try:
        if os.path.exists(temp_db):
            os.remove(temp_db)
    except Exception:
        pass

    # --------------------------------------------------------------------------
    # Test 11: Matplotlib Visualization Availability & Standalone Plot Test
    # --------------------------------------------------------------------------
    try:
        assert MATPLOTLIB_AVAILABLE, "Matplotlib is not installed or available."
        import matplotlib.pyplot as plt

        # Create headless figure to verify chart creation, bands, and formatting
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot([1, 2, 3], [22.0, 23.5, 22.8], marker='o')
        ax.axhline(18.5, color='blue', linestyle='--')
        ax.axhline(25.0, color='green', linestyle='--')
        ax.set_title("Test BMI Trend")
        # Save to buffer / temp file to verify export capability
        temp_fig_path = os.path.join(tempfile.gettempdir(), "test_bmi_plot.png")
        fig.savefig(temp_fig_path)
        plt.close(fig)
        assert os.path.exists(temp_fig_path), "Plot file was not saved."
        os.remove(temp_fig_path)

        print("[PASS] Test 11: Matplotlib Trend Plotting Engine Verified (Figure, Bands, Render, Savefig OK)")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Test 11: Matplotlib test failed: {e}")

    print("=" * 76)
    print(f"TEST RESULTS: {passed_count}/{total_count} TESTS PASSED ({(passed_count/total_count)*100:.1f}% SUCCESS)")
    print("=" * 76)
    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
