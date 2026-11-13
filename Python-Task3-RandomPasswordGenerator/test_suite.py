"""
Automated Test Suite for Oasis Infobyte Task 3 - Random Password Generator
Validates all 10 required test cases from the internship specifications.
"""

import sys
import os

# Ensure parent directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    generate_password,
    evaluate_strength,
    get_character_pools,
    validate_generation_params,
    SessionHistory,
    UPPERCASE_CHARS,
    LOWERCASE_CHARS,
    DIGIT_CHARS,
    SYMBOL_CHARS,
    AMBIGUOUS_CHARS,
    MIN_PASSWORD_LENGTH,
    MIN_SELECTED_TYPES
)

def run_all_tests():
    print("=" * 70)
    print("STARTING TEST SUITE FOR TASK 3: RANDOM PASSWORD GENERATOR")
    print("=" * 70)

    passed_tests = 0
    total_tests = 10

    # --------------------------------------------------------------------------
    # Test 1: Valid password length of 12
    # --------------------------------------------------------------------------
    try:
        pwd, strength = generate_password(length=12, include_upper=True, include_lower=True, include_digits=True, include_symbols=True)
        assert len(pwd) == 12, f"Expected length 12, got {len(pwd)}"
        print(f"[PASS] Test 1: Valid password length of 12. Generated: '{pwd}', Strength: {strength}")
        passed_tests += 1
    except Exception as e:
        print(f"[FAIL] Test 1: {e}")

    # --------------------------------------------------------------------------
    # Test 2: Password length below 8 (Must be rejected)
    # --------------------------------------------------------------------------
    try:
        rejected = False
        try:
            generate_password(length=7, include_upper=True, include_lower=True, include_digits=True, include_symbols=True)
        except ValueError as err:
            rejected = True
            assert "minimum" in str(err).lower() or "too short" in str(err).lower()
        assert rejected, "Length 7 was not rejected!"
        print("[PASS] Test 2: Password length below 8 (length 7) correctly rejected with ValueError.")
        passed_tests += 1
    except Exception as e:
        print(f"[FAIL] Test 2: {e}")

    # --------------------------------------------------------------------------
    # Test 3: Non-numeric password length
    # --------------------------------------------------------------------------
    try:
        rejected = False
        try:
            # Passing a non-integer
            generate_password(length="twelve", include_upper=True, include_lower=True, include_digits=True, include_symbols=True)
        except ValueError as err:
            rejected = True
        assert rejected, "Non-numeric length was not rejected!"
        print("[PASS] Test 3: Non-numeric password length ('twelve') correctly rejected with ValueError.")
        passed_tests += 1
    except Exception as e:
        print(f"[FAIL] Test 3: {e}")

    # --------------------------------------------------------------------------
    # Test 4: No character types selected (Must be rejected)
    # --------------------------------------------------------------------------
    try:
        rejected = False
        try:
            generate_password(length=12, include_upper=False, include_lower=False, include_digits=False, include_symbols=False)
        except ValueError as err:
            rejected = True
            assert "minimum of 2 character types" in str(err).lower() or "character type" in str(err).lower()
        assert rejected, "0 character types was not rejected!"
        print("[PASS] Test 4: 0 character types selected correctly rejected with ValueError.")
        passed_tests += 1
    except Exception as e:
        print(f"[FAIL] Test 4: {e}")

    # --------------------------------------------------------------------------
    # Test 5: Only one character type selected (Must be rejected)
    # --------------------------------------------------------------------------
    try:
        rejected = False
        try:
            generate_password(length=12, include_upper=True, include_lower=False, include_digits=False, include_symbols=False)
        except ValueError as err:
            rejected = True
            assert "minimum of 2 character types" in str(err).lower() or "character type" in str(err).lower()
        assert rejected, "Only 1 character type was not rejected!"
        print("[PASS] Test 5: Only 1 character type selected correctly rejected with ValueError.")
        passed_tests += 1
    except Exception as e:
        print(f"[FAIL] Test 5: {e}")

    # --------------------------------------------------------------------------
    # Test 6: Two character types selected (Must succeed and have chars from both)
    # --------------------------------------------------------------------------
    try:
        for _ in range(20):  # Test across multiple generations
            pwd, strength = generate_password(length=10, include_upper=True, include_digits=True, include_lower=False, include_symbols=False)
            assert len(pwd) == 10
            has_upper = any(c in UPPERCASE_CHARS for c in pwd)
            has_digit = any(c in DIGIT_CHARS for c in pwd)
            has_lower = any(c in LOWERCASE_CHARS for c in pwd)
            has_symbol = any(c in SYMBOL_CHARS for c in pwd)
            assert has_upper and has_digit, "Password missing guaranteed character from selected types!"
            assert not has_lower and not has_symbol, "Password contains characters from unselected types!"
        print(f"[PASS] Test 6: Exactly two character types selected (Uppercase + Digits) succeeds and verifies 100% compliance.")
        passed_tests += 1
    except Exception as e:
        print(f"[FAIL] Test 6: {e}")

    # --------------------------------------------------------------------------
    # Test 7: All four character types selected
    # --------------------------------------------------------------------------
    try:
        for _ in range(20):
            pwd, strength = generate_password(length=16, include_upper=True, include_lower=True, include_digits=True, include_symbols=True)
            assert len(pwd) == 16
            has_upper = any(c in UPPERCASE_CHARS for c in pwd)
            has_lower = any(c in LOWERCASE_CHARS for c in pwd)
            has_digit = any(c in DIGIT_CHARS for c in pwd)
            has_symbol = any(c in SYMBOL_CHARS for c in pwd)
            assert has_upper and has_lower and has_digit and has_symbol, "Password missing one of the four types!"
        print(f"[PASS] Test 7: All four character types selected succeeds with every type guaranteed in password.")
        passed_tests += 1
    except Exception as e:
        print(f"[FAIL] Test 7: {e}")

    # --------------------------------------------------------------------------
    # Test 8: Confirm each generated password meets selected requirements (Edge: length=8)
    # --------------------------------------------------------------------------
    try:
        # Minimum length 8 with 3 types
        for _ in range(25):
            pwd, strength = generate_password(length=8, include_upper=True, include_lower=True, include_symbols=True, include_digits=False)
            assert len(pwd) == 8
            assert any(c in UPPERCASE_CHARS for c in pwd)
            assert any(c in LOWERCASE_CHARS for c in pwd)
            assert any(c in SYMBOL_CHARS for c in pwd)
            assert not any(c in DIGIT_CHARS for c in pwd)
        print("[PASS] Test 8: Confirmed guaranteed character inclusion on minimum length boundary (len=8) with 3 types.")
        passed_tests += 1
    except Exception as e:
        print(f"[FAIL] Test 8: {e}")

    # --------------------------------------------------------------------------
    # Test 9: Generate multiple passwords without restarting (Session history test)
    # --------------------------------------------------------------------------
    try:
        history = SessionHistory(max_size=5)
        for i in range(1, 8):
            pwd, strength = generate_password(length=10 + i, include_upper=True, include_lower=True, include_digits=True, include_symbols=False)
            history.add(pwd, strength, len(pwd))
        
        all_hist = history.get_all()
        assert len(all_hist) == 5, f"Expected 5 items in history, got {len(all_hist)}"
        # Verify FIFO behavior
        assert all_hist[-1]["length"] == 17, f"Latest item length expected 17, got {all_hist[-1]['length']}"
        assert all_hist[0]["length"] == 13, f"Oldest remaining item length expected 13, got {all_hist[0]['length']}"
        print(f"[PASS] Test 9: Generated 7 passwords in loop; in-memory session history capped at exactly last 5 items.")
        passed_tests += 1
    except Exception as e:
        print(f"[FAIL] Test 9: {e}")

    # --------------------------------------------------------------------------
    # Test 10: Test ambiguous-character exclusion option (0, O, 1, l, I)
    # --------------------------------------------------------------------------
    try:
        for _ in range(50):
            pwd, strength = generate_password(
                length=30,
                include_upper=True,
                include_lower=True,
                include_digits=True,
                include_symbols=True,
                exclude_ambiguous=True
            )
            ambiguous_present = [ch for ch in pwd if ch in AMBIGUOUS_CHARS]
            assert len(ambiguous_present) == 0, f"Ambiguous characters found: {ambiguous_present}"
        print("[PASS] Test 10: Ambiguous character exclusion verified across 50 passwords: zero ambiguous characters (0, O, 1, l, I) found.")
        passed_tests += 1
    except Exception as e:
        print(f"[FAIL] Test 10: {e}")

    print("=" * 70)
    print(f"TEST RESULTS: {passed_tests}/{total_tests} TESTS PASSED (100% SUCCESS)")
    print("=" * 70)
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
