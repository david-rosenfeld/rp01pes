"""Agent factory and registry."""

from typing import Dict, Type
from pathlib import Path

from .base import BaseAgent
from ..core.exceptions import PESError


class AgentError(PESError):
    """Agent-specific error."""
    pass


_AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {}


def register_agent(name: str, agent_class: Type[BaseAgent]) -> None:
    """Register an agent adapter."""
    _AGENT_REGISTRY[name.lower()] = agent_class


def get_agent(
    agent_name: str,
    config: Dict,
    workspace: Path,
    backend_model: str = None
) -> BaseAgent:
    """Factory function to create agent instance."""
    agent_name = agent_name.lower()

    if agent_name not in _AGENT_REGISTRY:
        available = ', '.join(_AGENT_REGISTRY.keys())
        raise AgentError(f"Unknown agent: {agent_name}. Available: {available}")

    return _AGENT_REGISTRY[agent_name](config, workspace, backend_model)


def list_agents() -> list:
    """Get list of registered agents."""
    return list(_AGENT_REGISTRY.keys())
