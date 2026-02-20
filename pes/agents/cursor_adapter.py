"""Cursor agent adapter (placeholder - requires Cursor API access)."""

from typing import Dict

from .base import BaseAgent, AgentResult, AgentStatus


class CursorAdapter(BaseAgent):
    """
    Adapter for Cursor IDE agent.

    NOTE: This is a placeholder. Cursor integration requires:
    - Cursor API access (if available)
    - Or headless browser automation
    - Or VS Code extension API

    Configuration:
        cursor_api_key: API key for Cursor (if available)
        cursor_path: Path to Cursor executable
    """

    def _validate_config(self) -> None:
        """Validate Cursor configuration."""
        # Placeholder - no validation until API is available
        pass

    def _execute_task(
        self,
        task_prompt: str,
        files: Dict[str, str],
        **kwargs
    ) -> AgentResult:
        """Execute task using Cursor."""
        raise NotImplementedError(
            "Cursor adapter requires Cursor API or automation setup. "
            "No public API is currently available."
        )
