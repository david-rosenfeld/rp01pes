#!/usr/bin/env python3
"""
Validate the result of a task.

Usage:
    python validate_result.py --task task_01_factorial
    python validate_result.py --task task_02_bugfix --workspace ./my_workspace
"""

import argparse
import importlib.util
import sys
from pathlib import Path


TASKS = [
    'task_01_factorial',
    'task_02_bugfix',
    'task_03_test_generation',
    'task_04_refactor',
    'task_05_documentation',
]


def load_validator(task: str):
    """Load the validation module for a task."""
    script_dir = Path(__file__).parent
    package_dir = script_dir.parent
    validator_path = package_dir / "tasks" / task / "validate.py"

    if not validator_path.exists():
        raise ValueError(f"No validator for task: {task}")

    spec = importlib.util.spec_from_file_location("validator", validator_path)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)

    return validator


def validate_task(task: str, workspace: Path) -> tuple[bool, list[str]]:
    """Run validation for a task."""
    validator = load_validator(task)
    return validator.validate(workspace)


def main():
    parser = argparse.ArgumentParser(description="Validate task result")
    parser.add_argument(
        "--task", "-t",
        required=True,
        choices=TASKS,
        help="Task to validate"
    )
    parser.add_argument(
        "--workspace", "-w",
        type=Path,
        default=Path(__file__).parent.parent / "workspace",
        help="Workspace directory (default: ./workspace)"
    )

    args = parser.parse_args()

    if not args.workspace.exists():
        print(f"ERROR: Workspace not found: {args.workspace}")
        sys.exit(1)

    print(f"Validating {args.task} in {args.workspace}...")
    print()

    success, errors = validate_task(args.task, args.workspace)

    if success:
        print("=" * 50)
        print("PASS: All validation checks passed")
        print("=" * 50)
        sys.exit(0)
    else:
        print("=" * 50)
        print("FAIL: Validation errors:")
        print("=" * 50)
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
