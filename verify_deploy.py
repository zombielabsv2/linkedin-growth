#!/usr/bin/env python3
"""Pre-deployment verification for LinkedIn Growth.

Run before every push to master. Checks:
1. Syntax — all .py files compile cleanly
2. Requirements — requirements.txt exists and is parseable
3. Import chain — each module can be imported (with heavy deps mocked)
4. Tests — pytest suite passes

Exit code 1 on any failure.
"""

import subprocess
import sys
import os
import py_compile

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)

PASS = "PASS"
FAIL = "FAIL"
results = []


def log(check_name, passed, detail=""):
    status = PASS if passed else FAIL
    results.append((check_name, passed))
    marker = "+" if passed else "X"
    msg = f"  [{marker}] {check_name}: {status}"
    if detail:
        msg += f"  ({detail})"
    print(msg)


def collect_py_files():
    """Collect all .py files recursively, excluding __pycache__ and .git."""
    files = []
    for root, dirs, filenames in os.walk(PROJECT_ROOT):
        # Skip hidden dirs and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__" and d != ".pytest_cache"]
        for root_file in filenames:
            if root_file.endswith(".py"):
                files.append(os.path.join(root, root_file))
    return files


# -- 1. Syntax Check ----------------------------------------------------------
print("\n=== LinkedIn Growth: Pre-Deploy Verification ===\n")
print("1. Syntax Check")

py_files = collect_py_files()
syntax_ok = True
syntax_errors = []
for fpath in py_files:
    try:
        py_compile.compile(fpath, doraise=True)
    except py_compile.PyCompileError as e:
        syntax_ok = False
        rel = os.path.relpath(fpath, PROJECT_ROOT)
        syntax_errors.append(rel)

log("Syntax", syntax_ok,
    f"{len(py_files)} files OK" if syntax_ok
    else f"Errors in: {', '.join(syntax_errors)}")


# -- 2. Requirements Check ----------------------------------------------------
print("\n2. Requirements Check")

req_path = os.path.join(PROJECT_ROOT, "requirements.txt")
req_ok = False
req_count = 0
if os.path.exists(req_path):
    with open(req_path, "r") as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    req_count = len(lines)
    req_ok = req_count > 0

log("Requirements", req_ok,
    f"{req_count} packages" if req_ok else "requirements.txt missing or empty")


# -- 3. Import Chain -----------------------------------------------------------
print("\n3. Import Chain (with heavy deps mocked)")

# Modules and their external dependencies to mock
MODULES_TO_IMPORT = [
    ("scraper", ["requests", "bs4", "openpyxl"]),
    ("seed_data", []),  # pure Python data
    ("cloud_store", ["httpx"]),
    ("content_ops", ["streamlit", "streamlit.components", "streamlit.components.v1", "pandas", "plotly", "plotly.express", "plotly.graph_objects", "httpx"]),
    ("sync_content_to_supabase", ["httpx"]),
]

import_ok = True
import_errors = []

for mod_name, mocks in MODULES_TO_IMPORT:
    mock_lines = "; ".join(
        f"sys.modules['{m}'] = unittest.mock.MagicMock()"
        for m in mocks
    )
    if mock_lines:
        mock_lines = mock_lines + "; "
    cmd = [
        sys.executable, "-c",
        f"import unittest.mock; "
        f"import sys; "
        f"{mock_lines}"
        f"import {mod_name}; "
        f"print('OK')"
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30,
            cwd=PROJECT_ROOT,
            env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        )
        if result.returncode != 0:
            import_ok = False
            err_line = result.stderr.strip().splitlines()[-1] if result.stderr else "unknown error"
            import_errors.append(f"{mod_name}: {err_line}")
            log(f"Import {mod_name}", False, import_errors[-1])
        else:
            log(f"Import {mod_name}", True)
    except subprocess.TimeoutExpired:
        import_ok = False
        import_errors.append(f"{mod_name}: timeout")
        log(f"Import {mod_name}", False, "timeout")


# -- 4. Run pytest -------------------------------------------------------------
print("\n4. Test Suite")

tests_dir = os.path.join(PROJECT_ROOT, "tests")
test_ok = False
if os.path.isdir(tests_dir):
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120,
        cwd=PROJECT_ROOT,
    )
    test_ok = result.returncode == 0
    # Show summary lines
    for line in result.stdout.splitlines():
        if "passed" in line or "failed" in line or "error" in line:
            print(f"     {line}")
    if not test_ok and result.stderr:
        for line in result.stderr.strip().splitlines()[-5:]:
            print(f"     {line}")
else:
    print("     No tests/ directory found.")

log("Tests", test_ok, "all passed" if test_ok else "failures detected")


# -- Summary -------------------------------------------------------------------
print("\n" + "=" * 50)
passed = sum(1 for _, ok in results if ok)
total = len(results)
all_passed = all(ok for _, ok in results)

if all_passed:
    print(f"  ALL CHECKS PASSED ({passed}/{total})")
    print("  Safe to push.")
else:
    failed = [(name, ok) for name, ok in results if not ok]
    print(f"  {passed}/{total} PASSED, {len(failed)} FAILED:")
    for name, _ in failed:
        print(f"    - {name}")
    print("\n  DO NOT PUSH until all checks pass.")

print("=" * 50 + "\n")

sys.exit(0 if all_passed else 1)
