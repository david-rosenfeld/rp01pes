#!/usr/bin/env python3
"""Validation script for task_02_bugfix."""

import sys
import py_compile
from pathlib import Path


def validate(workspace: Path) -> tuple[bool, list[str]]:
    """
    Validate task_02_bugfix completion.

    Returns:
        Tuple of (success, list of error messages)
    """
    errors = []
    pagination_file = workspace / "pagination.py"

    # Check file exists
    if not pagination_file.exists():
        return False, ["pagination.py not found"]

    # Check syntax
    try:
        py_compile.compile(str(pagination_file), doraise=True)
    except py_compile.PyCompileError as e:
        return False, [f"Syntax error: {e}"]

    # Import and test
    sys.path.insert(0, str(workspace))
    try:
        if 'pagination' in sys.modules:
            del sys.modules['pagination']

        import pagination

        test_items = [1, 2, 3, 4, 5]

        # Test page 1
        result = pagination.paginate(test_items, page=1, per_page=2)
        if result['items'] != [1, 2]:
            errors.append(f"Page 1 items: got {result['items']}, expected [1, 2]")

        # Test page 2
        result = pagination.paginate(test_items, page=2, per_page=2)
        if result['items'] != [3, 4]:
            errors.append(f"Page 2 items: got {result['items']}, expected [3, 4]")

        # Test page 3
        result = pagination.paginate(test_items, page=3, per_page=2)
        if result['items'] != [5]:
            errors.append(f"Page 3 items: got {result['items']}, expected [5]")

        # Test has_next for page 1
        result = pagination.paginate(test_items, page=1, per_page=2)
        if not result['has_next']:
            errors.append("Page 1 should have has_next=True")

        # Test has_prev for page 1
        if result['has_prev']:
            errors.append("Page 1 should have has_prev=False")

    except Exception as e:
        errors.append(f"Runtime error: {type(e).__name__}: {e}")
    finally:
        sys.path.remove(str(workspace))
        if 'pagination' in sys.modules:
            del sys.modules['pagination']

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
