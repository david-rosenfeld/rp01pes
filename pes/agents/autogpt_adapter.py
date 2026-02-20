"""AutoGPT agent adapter."""

import subprocess
from pathlib import Path
from typing import Dict

from .base import BaseAgent, AgentResult, AgentStatus


class AutoGPTAdapter(BaseAgent):
    """
    Adapter for AutoGPT.

    AutoGPT can be run in CLI mode with a specific goal.

    NOTE: This adapter requires AutoGPT installation and configuration.
    AutoGPT needs specific setup with ai_settings.yaml for headless operation.

    Configuration:
        autogpt_path: Path to AutoGPT installation
        model: Backend model to use
    """

    def _validate_config(self) -> None:
        """Validate AutoGPT configuration."""
        self.autogpt_path = Path(self.config.get('autogpt_path', './AutoGPT'))

        if not self.autogpt_path.exists():
            raise ValueError(
                f"AutoGPT not found at {self.autogpt_path}. "
                f"Clone from https://github.com/Significant-Gravitas/AutoGPT"
            )

    def _execute_task(
        self,
        task_prompt: str,
        files: Dict[str, str],
        **kwargs
    ) -> AgentResult:
        """Execute task using AutoGPT."""
        # AutoGPT requires specific setup with ai_settings.yaml
        # This is a placeholder implementation
        raise NotImplementedError(
            "AutoGPT adapter requires additional setup. "
            "AutoGPT needs ai_settings.yaml configuration for headless operation."
        )
