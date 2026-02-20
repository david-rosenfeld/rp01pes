#!/usr/bin/env python3
"""
Record a trial result interactively.

Usage:
    python record_result.py
"""

import json
from datetime import datetime
from pathlib import Path


TASKS = [
    'task_01_factorial',
    'task_02_bugfix',
    'task_03_test_generation',
    'task_04_refactor',
    'task_05_documentation',
]

AGENTS = ['cursor', 'kiro']


def get_input(prompt: str, valid_options: list = None, input_type: type = str):
    """Get validated input from user."""
    while True:
        value = input(prompt).strip()
        if valid_options and value not in valid_options:
            print(f"  Invalid. Choose from: {', '.join(valid_options)}")
            continue
        if input_type == int:
            try:
                return int(value)
            except ValueError:
                print("  Please enter a number.")
                continue
        if input_type == float:
            try:
                return float(value)
            except ValueError:
                print("  Please enter a number.")
                continue
        if input_type == bool:
            if value.lower() in ['y', 'yes', 'true', '1']:
                return True
            elif value.lower() in ['n', 'no', 'false', '0']:
                return False
            else:
                print("  Please enter y/n.")
                continue
        return value


def main():
    script_dir = Path(__file__).parent
    results_dir = script_dir.parent / "results"

    print("=" * 50)
    print("Record Trial Result")
    print("=" * 50)
    print()

    # Get trial info
    agent = get_input(f"Agent ({'/'.join(AGENTS)}): ", AGENTS)
    task = get_input(f"Task ({'/'.join([t.replace('task_0', 't') for t in TASKS])}): ")

    # Normalize task input
    if task.startswith('t') and len(task) == 2:
        task_num = task[1]
        task = [t for t in TASKS if f"task_0{task_num}" in t][0]
    elif task not in TASKS:
        print(f"Unknown task: {task}")
        return

    # Count existing trials for this agent-task
    agent_dir = results_dir / agent
    existing = list(agent_dir.glob(f"{agent}_{task.split('_')[1]}*.json")) if agent_dir.exists() else []
    trial_num = len(existing) + 1

    trial_id = f"{agent}_{task.split('_')[1]}_{trial_num:03d}"
    print(f"\nTrial ID: {trial_id}")

    # Get results
    success = get_input("Success (y/n): ", input_type=bool)
    duration = get_input("Duration (seconds): ", input_type=float)
    iterations = get_input("Iterations: ", input_type=int)
    interventions = get_input("User interventions: ", input_type=int)
    timeout = get_input("Timeout reached (y/n): ", input_type=bool)
    notes = input("Notes (optional): ").strip()

    # Build result
    result = {
        "trial_id": trial_id,
        "agent": agent,
        "task": task,
        "trial_number": trial_num,
        "success": success,
        "duration_seconds": duration,
        "iterations": iterations,
        "user_interventions": interventions,
        "timeout": timeout,
        "notes": notes,
        "recorded_at": datetime.now().isoformat()
    }

    # Save
    agent_dir.mkdir(parents=True, exist_ok=True)
    output_file = agent_dir / f"{trial_id}.json"

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\nSaved to: {output_file}")
    print("\nResult:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
