#!/usr/bin/env python3
"""
Summarize all recorded results.

Usage:
    python summarize_results.py
"""

import json
from pathlib import Path
from collections import defaultdict


TASKS = [
    'task_01_factorial',
    'task_02_bugfix',
    'task_03_test_generation',
    'task_04_refactor',
    'task_05_documentation',
]

AGENTS = ['cursor', 'kiro']


def load_results(results_dir: Path) -> list[dict]:
    """Load all result JSON files."""
    results = []
    for agent in AGENTS:
        agent_dir = results_dir / agent
        if not agent_dir.exists():
            continue
        for result_file in agent_dir.glob("*.json"):
            try:
                with open(result_file) as f:
                    data = json.load(f)
                    results.append(data)
            except Exception as e:
                print(f"Warning: Failed to load {result_file}: {e}")
    return results


def summarize(results: list[dict]) -> None:
    """Print summary statistics."""
    if not results:
        print("No results found.")
        return

    # Group by agent and task
    by_agent_task = defaultdict(list)
    for r in results:
        key = (r['agent'], r['task'])
        by_agent_task[key].append(r)

    # Print summary table header
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    # Success rates by task
    print("\n### Success Rates ###\n")
    print(f"{'Task':<25} {'Cursor':<15} {'Kiro':<15}")
    print("-" * 55)

    for task in TASKS:
        cursor_results = by_agent_task.get(('cursor', task), [])
        kiro_results = by_agent_task.get(('kiro', task), [])

        cursor_success = sum(1 for r in cursor_results if r.get('success', False))
        kiro_success = sum(1 for r in kiro_results if r.get('success', False))

        cursor_str = f"{cursor_success}/{len(cursor_results)}" if cursor_results else "-"
        kiro_str = f"{kiro_success}/{len(kiro_results)}" if kiro_results else "-"

        task_short = task.replace('task_', '').replace('_', ' ').title()
        print(f"{task_short:<25} {cursor_str:<15} {kiro_str:<15}")

    # Average durations
    print("\n### Average Duration (seconds) ###\n")
    print(f"{'Task':<25} {'Cursor':<15} {'Kiro':<15}")
    print("-" * 55)

    for task in TASKS:
        cursor_results = by_agent_task.get(('cursor', task), [])
        kiro_results = by_agent_task.get(('kiro', task), [])

        cursor_durations = [r['duration_seconds'] for r in cursor_results if 'duration_seconds' in r]
        kiro_durations = [r['duration_seconds'] for r in kiro_results if 'duration_seconds' in r]

        cursor_avg = f"{sum(cursor_durations) / len(cursor_durations):.1f}" if cursor_durations else "-"
        kiro_avg = f"{sum(kiro_durations) / len(kiro_durations):.1f}" if kiro_durations else "-"

        task_short = task.replace('task_', '').replace('_', ' ').title()
        print(f"{task_short:<25} {cursor_avg:<15} {kiro_avg:<15}")

    # Average iterations
    print("\n### Average Iterations ###\n")
    print(f"{'Task':<25} {'Cursor':<15} {'Kiro':<15}")
    print("-" * 55)

    for task in TASKS:
        cursor_results = by_agent_task.get(('cursor', task), [])
        kiro_results = by_agent_task.get(('kiro', task), [])

        cursor_iters = [r['iterations'] for r in cursor_results if 'iterations' in r]
        kiro_iters = [r['iterations'] for r in kiro_results if 'iterations' in r]

        cursor_avg = f"{sum(cursor_iters) / len(cursor_iters):.1f}" if cursor_iters else "-"
        kiro_avg = f"{sum(kiro_iters) / len(kiro_iters):.1f}" if kiro_iters else "-"

        task_short = task.replace('task_', '').replace('_', ' ').title()
        print(f"{task_short:<25} {cursor_avg:<15} {kiro_avg:<15}")

    # Overall summary
    print("\n### Overall ###\n")

    cursor_all = [r for r in results if r['agent'] == 'cursor']
    kiro_all = [r for r in results if r['agent'] == 'kiro']

    cursor_total_success = sum(1 for r in cursor_all if r.get('success', False))
    kiro_total_success = sum(1 for r in kiro_all if r.get('success', False))

    print(f"Cursor: {cursor_total_success}/{len(cursor_all)} tasks succeeded ({100*cursor_total_success/len(cursor_all):.0f}%)" if cursor_all else "Cursor: No results")
    print(f"Kiro: {kiro_total_success}/{len(kiro_all)} tasks succeeded ({100*kiro_total_success/len(kiro_all):.0f}%)" if kiro_all else "Kiro: No results")

    # Interventions
    cursor_interventions = sum(r.get('user_interventions', 0) for r in cursor_all)
    kiro_interventions = sum(r.get('user_interventions', 0) for r in kiro_all)
    print(f"\nUser interventions - Cursor: {cursor_interventions}, Kiro: {kiro_interventions}")

    print("\n" + "=" * 80)


def main():
    script_dir = Path(__file__).parent
    results_dir = script_dir.parent / "results"

    if not results_dir.exists():
        print(f"Results directory not found: {results_dir}")
        return

    results = load_results(results_dir)
    summarize(results)


if __name__ == "__main__":
    main()
