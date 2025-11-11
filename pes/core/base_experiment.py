"""
Base experiment class for all preliminary experiments.

This module defines the abstract base class that all experiment
implementations must inherit from, providing common functionality
and defining the required interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path
import time
import json
from datetime import datetime

from ..core.logging import get_logger
from ..core.config import ConfigurationManager
from ..core.exceptions import ExperimentError


class BaseExperiment(ABC):
    """
    Abstract base class for all preliminary experiments.
    
    All experiment implementations (PE01-PE10) must inherit from this class
    and implement the required abstract methods. This class provides common
    functionality for configuration, logging, result storage, and execution.
    
    Implements REQ-3.5 (Experiment Execution Engine).
    """
    
    def __init__(self, config: ConfigurationManager, experiment_id: str):
        """
        Initialize base experiment.
        
        Args:
            config: Configuration manager instance
            experiment_id: Unique identifier for this experiment instance
        """
        self.config = config
        self.experiment_id = experiment_id
        self.experiment_type = self.__class__.__name__
        
        # Initialize logger
        log_dir = config.get('execution.log_dir', 'logs')
        log_level = config.get('execution.log_level', 'INFO')
        self.logger = get_logger(
            f"{self.experiment_type}.{experiment_id}",
            log_dir=log_dir,
            level=log_level
        )
        
        # Initialize result storage
        self.results = {
            'experiment_id': experiment_id,
            'experiment_type': self.experiment_type,
            'status': 'initialized',
            'start_time': None,
            'end_time': None,
            'duration_seconds': None,
            'data': {}
        }
    
    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """
        Execute the experiment.
        
        This is the main entry point that must be implemented by all
        experiment subclasses. It should perform the experiment logic
        and return results.
        
        Returns:
            Dictionary containing experiment results
        
        Raises:
            ExperimentError: If experiment execution fails
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get human-readable description of the experiment.
        
        Returns:
            Description string
        """
        pass
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute experiment with timing, error handling, and result storage.
        
        This method wraps the run() method with common functionality:
        - Timing
        - Error handling
        - Result storage
        - Status tracking
        
        Returns:
            Dictionary containing experiment results
        """
        # Log experiment start
        self.logger.experiment_start(self.experiment_id, self.experiment_type)
        self.results['start_time'] = datetime.now().isoformat()
        self.results['status'] = 'running'
        
        # Record start time
        start_time = time.time()
        
        try:
            # Execute experiment-specific logic
            experiment_data = self.run()
            
            # Update results with experiment data
            self.results['data'] = experiment_data
            self.results['status'] = 'completed'
            
        except Exception as e:
            # Log error and update status
            self.logger.error(f"Experiment failed: {str(e)}")
            self.results['status'] = 'failed'
            self.results['error'] = str(e)
            self.results['error_type'] = type(e).__name__
            
            # Re-raise as ExperimentError
            raise ExperimentError(f"Experiment {self.experiment_id} failed: {e}") from e
        
        finally:
            # Record end time and duration
            end_time = time.time()
            duration = end_time - start_time
            
            self.results['end_time'] = datetime.now().isoformat()
            self.results['duration_seconds'] = duration
            
            # Log completion
            self.logger.experiment_end(
                self.experiment_id,
                self.results['status'],
                duration
            )
            
            # Save results to file
            self._save_results()
        
        return self.results
    
    def _save_results(self) -> None:
        """
        Save experiment results to JSON file.
        
        Implements REQ-3.7.1 (Result Storage Format).
        """
        # Get output directory from config
        output_dir = Path(self.config.get('output.directory', 'results'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.experiment_type}_{self.experiment_id}_{timestamp}.json"
        filepath = output_dir / filename
        
        # Write results to JSON file
        try:
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            self.logger.info(f"Results saved to: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
    
    def log_info(self, message: str, **kwargs):
        """Convenience method to log info message."""
        self.logger.info(message, **kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Convenience method to log debug message."""
        self.logger.debug(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Convenience method to log warning message."""
        self.logger.warning(message, **kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Convenience method to log error message."""
        self.logger.error(message, **kwargs)
