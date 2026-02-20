#!/usr/bin/env python3
"""Validation script for task_04_refactor."""

import sys
import ast
import py_compile
from pathlib import Path


# Reference outputs
SALES_TEST_DATA = [
    {'product': 'Widget', 'amount': 25.00},
    {'product': 'Gadget', 'amount': 49.99},
]

INVENTORY_TEST_DATA = [
    {'name': 'Widget', 'quantity': 100},
    {'name': 'Gadget', 'quantity': 50},
]

EXPECTED_SALES_OUTPUT = """==================================================
SALES REPORT
==================================================

  Widget: $25.00
  Gadget: $49.99

--------------------------------------------------
  TOTAL: $74.99
=================================================="""

EXPECTED_INVENTORY_OUTPUT = """==================================================
INVENTORY REPORT
==================================================

  Widget: 100 units
  Gadget: 50 units

--------------------------------------------------
  TOTAL ITEMS: 150
=================================================="""


def validate(workspace: Path) -> tuple[bool, list[str]]:
    """
    Validate task_04_refactor completion.

    Returns:
        Tuple of (success, list of error messages)
    """
    errors = []
    report_file = workspace / "report_generator.py"

    # Check file exists
    if not report_file.exists():
        return False, ["report_generator.py not found"]

    # Check syntax
    try:
        py_compile.compile(str(report_file), doraise=True)
    except py_compile.PyCompileError as e:
        return False, [f"Syntax error: {e}"]

    # Count functions (should be > 2 after adding helper)
    try:
        with open(report_file) as f:
            tree = ast.parse(f.read())

        functions = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]

        if len(functions) <= 2:
            errors.append(f"Found {len(functions)} functions, expected >2 (helper should be added)")
    except Exception as e:
        errors.append(f"Failed to parse file: {e}")

    # Import and test output matching
    sys.path.insert(0, str(workspace))
    try:
        if 'report_generator' in sys.modules:
            del sys.modules['report_generator']

        import report_generator

        # Test sales report output
        sales_output = report_generator.generate_sales_report(SALES_TEST_DATA)
        if sales_output != EXPECTED_SALES_OUTPUT:
            errors.append("generate_sales_report output differs from expected")
            errors.append(f"Got:\n{sales_output}")
            errors.append(f"Expected:\n{EXPECTED_SALES_OUTPUT}")

        # Test inventory report output
        inventory_output = report_generator.generate_inventory_report(INVENTORY_TEST_DATA)
        if inventory_output != EXPECTED_INVENTORY_OUTPUT:
            errors.append("generate_inventory_report output differs from expected")
            errors.append(f"Got:\n{inventory_output}")
            errors.append(f"Expected:\n{EXPECTED_INVENTORY_OUTPUT}")

    except Exception as e:
        errors.append(f"Runtime error: {type(e).__name__}: {e}")
    finally:
        sys.path.remove(str(workspace))
        if 'report_generator' in sys.modules:
            del sys.modules['report_generator']

    return len(errors) == 0, errors


if __name__ == "__main__":
    workspace = Path.cwd()
    if len(sys.argv) > 1:
        workspace = Path(sys.argv[1])

    success, errors = validate(workspace)

    if success:
        print("PASS: All validation checks passed")
        sys.exit(0)
    else:
        print("FAIL: Validation errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
