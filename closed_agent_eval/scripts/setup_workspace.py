#!/usr/bin/env python3
"""
Set up workspace for a specific task.

Usage:
    python setup_workspace.py --task task_01_factorial
    python setup_workspace.py --task task_02_bugfix --output ./my_workspace
"""

import argparse
import shutil
from pathlib import Path


TASKS = [
    'task_01_factorial',
    'task_02_bugfix',
    'task_03_test_generation',
    'task_04_refactor',
    'task_05_documentation',
]


def setup_workspace(task: str, output: Path) -> None:
    """Copy initial files for a task to the workspace."""
    script_dir = Path(__file__).parent
    package_dir = script_dir.parent
    task_dir = package_dir / "tasks" / task
    initial_dir = task_dir / "initial"

    if not task_dir.exists():
        raise ValueError(f"Task not found: {task}")

    if not initial_dir.exists():
        raise ValueError(f"No initial files for task: {task}")

    # Clean and create workspace
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    # Copy initial files
    for src_file in initial_dir.iterdir():
        if src_file.is_file():
            shutil.copy(src_file, output / src_file.name)

    print(f"Workspace ready: {output}")
    print(f"Files copied:")
    for f in output.iterdir():
        print(f"  - {f.name}")

    # Show prompt location
    prompt_file = task_dir / "PROMPT.txt"
    print(f"\nPrompt file: {prompt_file}")
    print("\n--- PROMPT ---")
    print(prompt_file.read_text())
    print("--- END PROMPT ---")


def main():
    parser = argparse.ArgumentParser(description="Set up workspace for a task")
    parser.add_argument(
        "--task", "-t",
        required=True,
        choices=TASKS,
        help="Task to set up"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path(__file__).parent.parent / "workspace",
        help="Output directory (default: ./workspace)"
    )

    args = parser.parse_args()
    setup_workspace(args.task, args.output)


if __name__ == "__main__":
    main()
