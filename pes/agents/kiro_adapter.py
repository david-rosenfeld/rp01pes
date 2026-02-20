"""Amazon Kiro agent adapter (placeholder - requires Kiro API)."""

from typing import Dict

from .base import BaseAgent, AgentResult, AgentStatus


class KiroAdapter(BaseAgent):
    """
    Adapter for Amazon Kiro.

    Kiro uses Claude Sonnet 4 as its backend.

    NOTE: This is a placeholder. Kiro integration requires:
    - Amazon Kiro API access
    - API documentation and credentials

    Configuration:
        kiro_api_key: API key for Kiro
    """

    def _validate_config(self) -> None:
        """Validate Kiro configuration."""
        # Placeholder - no validation until API is available
        pass

    def _execute_task(
        self,
        task_prompt: str,
        files: Dict[str, str],
        **kwargs
    ) -> AgentResult:
        """Execute task using Kiro."""
        raise NotImplementedError(
            "Kiro adapter requires Amazon Kiro API access. "
            "No public API documentation is currently available."
        )
