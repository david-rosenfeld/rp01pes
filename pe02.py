#!/usr/bin/env python3
"""
PE02: Model Selection - Prompt-Based

Standalone program to execute the Model Selection preliminary experiment.
This program tests multiple candidate models on a benchmark task and
selects the top performers for use in main experiments.

Usage:
    python pe02.py [config_file]
    
Example:
    python pe02.py configs/pe02_config.yaml
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pes.core.config import load_config
from pes.core.logging import get_logger
from pes.core.exceptions import PESError
from pes.experiments.pe02_model_selection import ModelSelectionExperiment


def main():
    """
    Main entry point for PE02 experiment.
    
    This function:
    1. Loads configuration
    2. Initializes the experiment
    3. Executes the experiment
    4. Reports results
    """
    # Initialize logger
    logger = get_logger("PE02")
    
    try:
        # Determine config file
        if len(sys.argv) > 1:
            config_file = sys.argv[1]
        else:
            # Look for default config
            default_configs = [
                'configs/pe02_config.yaml',
                'configs/pe02_config.json',
                'config.yaml',
                'config.json'
            ]
            
            config_file = None
            for path in default_configs:
                if Path(path).exists():
                    config_file = path
                    break
            
            if not config_file:
                logger.error(
                    "No configuration file specified and no default found. "
                    "Usage: python pe02.py <config_file>"
                )
                return 1
        
        logger.info(f"Loading configuration from: {config_file}")
        
        # Load configuration
        config = load_config(config_file)
        
        # Validate required sections
        config.validate_required_sections('experiments', 'output')
        
        logger.info("Configuration loaded successfully")
        logger.info("="*60)
        logger.info("PE02: Model Selection - Prompt-Based")
        logger.info("="*60)
        
        # Create and execute experiment
        experiment = ModelSelectionExperiment(config, experiment_id="PE02")
        
        logger.info(f"Description: {experiment.get_description()}")
        logger.info("")
        
        # Execute experiment
        results = experiment.execute()
        
        # Report summary
        logger.info("="*60)
        logger.info("Experiment Summary")
        logger.info("="*60)
        logger.info(f"Status: {results['status']}")
        logger.info(f"Duration: {results['duration_seconds']:.2f} seconds")
        
        if results['status'] == 'completed':
            data = results['data']
            logger.info(f"Candidates Tested: {data['candidates_tested']}")
            logger.info(f"Models Selected: {len(data['selected_models'])}")
            logger.info("")
            logger.info("Top Models:")
            for model in data['selected_models']:
                logger.info(
                    f"  - {model['model_name']} "
                    f"(score: {model['composite_score']:.3f})"
                )
        
        logger.info("="*60)
        logger.info(f"Results saved to: {config.get('output.directory', 'results')}")
        
        return 0
        
    except PESError as e:
        logger.error(f"Experiment failed: {e}")
        return 1
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
