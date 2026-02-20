#!/usr/bin/env python3
"""Validation script for task_01_factorial."""

import sys
import py_compile
from pathlib import Path


def validate(workspace: Path) -> tuple[bool, list[str]]:
    """
    Validate task_01_factorial completion.

    Returns:
        Tuple of (success, list of error messages)
    """
    errors = []
    math_utils = workspace / "math_utils.py"

    # Check file exists
    if not math_utils.exists():
        return False, ["math_utils.py not found"]

    # Check syntax
    try:
        py_compile.compile(str(math_utils), doraise=True)
    except py_compile.PyCompileError as e:
        return False, [f"Syntax error: {e}"]

    # Import and test
    sys.path.insert(0, str(workspace))
    try:
        # Clear any cached import
        if 'math_utils' in sys.modules:
            del sys.modules['math_utils']

        import math_utils

        # Check factorial exists
        if not hasattr(math_utils, 'factorial'):
            errors.append("Function 'factorial' not found")
            return False, errors

        factorial = math_utils.factorial

        # Check docstring
        if not factorial.__doc__:
            errors.append("factorial missing docstring")

        # Test factorial(0) == 1
        try:
            result = factorial(0)
            if result != 1:
                errors.append(f"factorial(0) returned {result}, expected 1")
        except Exception as e:
            errors.append(f"factorial(0) raised {type(e).__name__}: {e}")

        # Test factorial(5) == 120
        try:
            result = factorial(5)
            if result != 120:
                errors.append(f"factorial(5) returned {result}, expected 120")
        except Exception as e:
            errors.append(f"factorial(5) raised {type(e).__name__}: {e}")

        # Test factorial(1) == 1
        try:
            result = factorial(1)
            if result != 1:
                errors.append(f"factorial(1) returned {result}, expected 1")
        except Exception as e:
            errors.append(f"factorial(1) raised {type(e).__name__}: {e}")

        # Test factorial(-1) raises ValueError
        try:
            factorial(-1)
            errors.append("factorial(-1) should raise ValueError")
        except ValueError:
            pass  # Expected
        except Exception as e:
            errors.append(f"factorial(-1) raised {type(e).__name__}, expected ValueError")

        # Test existing functions still work
        try:
            if math_utils.add(2, 3) != 5:
                errors.append("add(2, 3) broken")
            if math_utils.multiply(2, 3) != 6:
                errors.append("multiply(2, 3) broken")
        except Exception as e:
            errors.append(f"Existing functions broken: {e}")

    finally:
        sys.path.remove(str(workspace))
        if 'math_utils' in sys.modules:
            del sys.modules['math_utils']

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
