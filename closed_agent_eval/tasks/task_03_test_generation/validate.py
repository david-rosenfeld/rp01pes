#!/usr/bin/env python3
"""Validation script for task_03_test_generation."""

import sys
import ast
import subprocess
import py_compile
from pathlib import Path


def validate(workspace: Path) -> tuple[bool, list[str]]:
    """
    Validate task_03_test_generation completion.

    Returns:
        Tuple of (success, list of error messages)
    """
    errors = []
    test_file = workspace / "test_validator.py"

    # Check test file exists
    if not test_file.exists():
        return False, ["test_validator.py not found"]

    # Check syntax
    try:
        py_compile.compile(str(test_file), doraise=True)
    except py_compile.PyCompileError as e:
        return False, [f"Syntax error: {e}"]

    # Count test functions using AST
    try:
        with open(test_file) as f:
            tree = ast.parse(f.read())

        test_functions = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
        ]

        if len(test_functions) < 9:
            errors.append(f"Found {len(test_functions)} test functions, expected at least 9")
    except Exception as e:
        errors.append(f"Failed to parse test file: {e}")

    # Check that tests import validator
    try:
        with open(test_file) as f:
            content = f.read()
        if 'validator' not in content and 'validate_' not in content:
            errors.append("Tests don't appear to import or use validator module")
    except Exception as e:
        errors.append(f"Failed to read test file: {e}")

    # Run pytest
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            errors.append(f"pytest failed (exit code {result.returncode})")
            # Add first few lines of output for context
            output_lines = result.stdout.split('\n')[:10]
            if result.stderr:
                output_lines.extend(result.stderr.split('\n')[:5])
            errors.append("Output: " + '\n'.join(output_lines))
    except subprocess.TimeoutExpired:
        errors.append("pytest timed out after 30 seconds")
    except FileNotFoundError:
        errors.append("pytest not found - install with: pip install pytest")
    except Exception as e:
        errors.append(f"Failed to run pytest: {e}")

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
