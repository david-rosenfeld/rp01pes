#!/usr/bin/env python3
"""
Run All Preliminary Experiments

Executes all implemented preliminary experiments (PE01-PE10, excluding PE03)
using the mock provider and reports results.

Usage:
    python run_all_experiments.py [config_file]

Example:
    python run_all_experiments.py configs/config.yaml
"""

import sys
import json
import traceback
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pes.core.config import load_config
from pes.core.logging import get_logger
from pes.core.exceptions import PESError


# Experiment registry: (id, module_path, class_name, config_key)
EXPERIMENTS = [
    ("PE01", "pes.experiments.pe01_languageeffect", "LanguageEffectExperiment"),
    ("PE02", "pes.experiments.pe02_model_selection", "ModelSelectionExperiment"),
    # PE03 deferred - agentic integration not ready
    ("PE04", "pes.experiments.pe04_temperatureoptimization", "TemperatureOptimizationExperiment"),
    ("PE05", "pes.experiments.pe05_maxtokendetermination", "MaxTokenDeterminationExperiment"),
    ("PE06", "pes.experiments.pe06_stopsequence", "StopSequenceExperiment"),
    ("PE07", "pes.experiments.pe07_promptstrategy", "PromptStrategyExperiment"),
    ("PE08", "pes.experiments.pe08_controlcondition", "ControlConditionExperiment"),
    ("PE09", "pes.experiments.pe09_tokenbudget", "TokenBudgetExperiment"),
    ("PE10", "pes.experiments.pe10_poweranalysis", "PowerAnalysisExperiment"),
]


def import_experiment(module_path, class_name):
    """Dynamically import an experiment class."""
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def summarize_results(exp_id, results):
    """Extract key findings from experiment results for display."""
    data = results.get('data', {})

    if exp_id == "PE01":
        rec = data.get('recommendation', {})
        decision = rec.get('decision', 'N/A')
        models_tested = len(data.get('model_results', {}))
        return f"Decision: {decision} | Models tested: {models_tested}"

    elif exp_id == "PE02":
        selected = data.get('selected_models', [])
        names = [m.get('model_name', '?') for m in selected]
        return f"Selected {len(selected)} models: {', '.join(names)}"

    elif exp_id == "PE04":
        recs = data.get('recommendations', {})
        summary_parts = []
        for task_type, rec in recs.items():
            temp = rec.get('optimal_temperature', '?')
            summary_parts.append(f"{task_type}={temp}")
        return f"Optimal temperatures: {', '.join(summary_parts) or 'N/A'}"

    elif exp_id == "PE05":
        recs = data.get('recommendations', {})
        summary_parts = []
        for task_type, rec in recs.items():
            limit = rec.get('max_tokens', rec.get('recommended_limit', '?'))
            summary_parts.append(f"{task_type}={limit}")
        return f"Recommended limits: {', '.join(summary_parts) or 'N/A'}"

    elif exp_id == "PE06":
        final = data.get('final_sequences', data.get('validated_sequences', {}))
        summary_parts = []
        for task_type, seq_info in final.items():
            if isinstance(seq_info, dict):
                seq = seq_info.get('sequence', seq_info.get('best_sequence', '?'))
            else:
                seq = str(seq_info)
            summary_parts.append(f"{task_type}: {repr(seq)}")
        return f"Stop sequences: {'; '.join(summary_parts) or 'N/A'}"

    elif exp_id == "PE07":
        selected = data.get('selected_strategy', {})
        name = selected.get('strategy_name', selected.get('name', 'N/A'))
        return f"Selected strategy: {name}"

    elif exp_id == "PE08":
        recs = data.get('recommendations', {})
        summary_parts = []
        for model_type, rec in recs.items():
            variant = rec.get('recommended_variant', rec.get('variant', '?'))
            summary_parts.append(f"{model_type}: {variant}")
        return f"Control conditions: {'; '.join(summary_parts) or 'N/A'}"

    elif exp_id == "PE09":
        alloc = data.get('final_allocation', data.get('budget_configuration', {}))
        scheme = alloc.get('scheme_name', alloc.get('scheme', 'N/A'))
        return f"Selected scheme: {scheme}"

    elif exp_id == "PE10":
        recs = data.get('recommendations', {})
        overall = recs.get('overall', {})
        n = overall.get('conservative_n', overall.get('max_inflated_n', '?'))
        return f"Recommended sample size: {n}"

    return f"Completed ({len(data)} result keys)"


def main():
    logger = get_logger("RunAll")

    # Determine config file
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = 'configs/config.yaml'
        if not Path(config_file).exists():
            logger.error(f"Default config not found: {config_file}")
            return 1

    logger.info(f"Loading configuration from: {config_file}")
    config = load_config(config_file)

    # Track results
    run_results = []
    start_time = datetime.now()

    print("\n" + "=" * 70)
    print("  PRELIMINARY EXPERIMENTS SYSTEM - Batch Execution")
    print(f"  Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Config:  {config_file}")
    print(f"  Mode:    Mock Provider (no API calls)")
    print("=" * 70 + "\n")

    for exp_id, module_path, class_name in EXPERIMENTS:
        print(f"\n{'-' * 70}")
        print(f"  {exp_id}: Running...")
        print(f"{'-' * 70}")

        try:
            # Import and instantiate
            ExperimentClass = import_experiment(module_path, class_name)
            experiment = ExperimentClass(config, experiment_id=exp_id)

            # Execute
            results = experiment.execute()
            status = results.get('status', 'unknown')
            duration = results.get('duration_seconds', 0)

            if status == 'completed':
                summary = summarize_results(exp_id, results)
                print(f"  Status:   COMPLETED")
                print(f"  Duration: {duration:.2f}s")
                print(f"  Result:   {summary}")
                run_results.append({
                    'experiment': exp_id,
                    'status': 'completed',
                    'duration': duration,
                    'summary': summary,
                })
            else:
                print(f"  Status:   {status.upper()}")
                print(f"  Duration: {duration:.2f}s")
                error = results.get('error', 'Unknown error')
                print(f"  Error:    {error}")
                run_results.append({
                    'experiment': exp_id,
                    'status': status,
                    'duration': duration,
                    'error': str(error),
                })

        except Exception as e:
            print(f"  Status:   FAILED")
            print(f"  Error:    {e}")
            traceback.print_exc()
            run_results.append({
                'experiment': exp_id,
                'status': 'failed',
                'error': str(e),
            })

    # Print summary
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    completed = sum(1 for r in run_results if r['status'] == 'completed')
    failed = sum(1 for r in run_results if r['status'] != 'completed')

    print(f"\n\n{'=' * 70}")
    print("  EXECUTION SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total experiments: {len(run_results)}")
    print(f"  Completed:         {completed}")
    print(f"  Failed:            {failed}")
    print(f"  Total duration:    {total_duration:.2f}s")
    print(f"  Finished:          {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Results table
    print(f"  {'Experiment':<12} {'Status':<12} {'Duration':<10} {'Key Finding'}")
    print(f"  {'-' * 12} {'-' * 12} {'-' * 10} {'-' * 34}")
    for r in run_results:
        status_str = r['status'].upper()
        duration_str = f"{r.get('duration', 0):.2f}s" if 'duration' in r else "N/A"
        finding = r.get('summary', r.get('error', 'N/A'))
        # Truncate long findings
        if len(finding) > 60:
            finding = finding[:57] + "..."
        print(f"  {r['experiment']:<12} {status_str:<12} {duration_str:<10} {finding}")

    print(f"\n  Results saved to: {config.get('output.directory', 'results')}/")
    print(f"{'=' * 70}\n")

    # Save batch summary
    summary_path = Path(config.get('output.directory', 'results')) / f"batch_run_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w') as f:
        json.dump({
            'run_started': start_time.isoformat(),
            'run_finished': end_time.isoformat(),
            'total_duration_seconds': total_duration,
            'config_file': config_file,
            'experiments': run_results,
        }, f, indent=2)
    print(f"  Batch summary: {summary_path}")

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
