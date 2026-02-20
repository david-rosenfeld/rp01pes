"""Agent integration module."""

from .base import BaseAgent, AgentResult, AgentStatus, ToolCall
from .factory import get_agent, register_agent, list_agents, AgentError
from .sandbox import temporary_workspace

# Import and register adapters
try:
    from .aider_adapter import AiderAdapter
    register_agent('aider', AiderAdapter)
except ImportError:
    AiderAdapter = None

# Placeholder adapters (will raise NotImplementedError when used)
try:
    from .cursor_adapter import CursorAdapter
    register_agent('cursor', CursorAdapter)
except ImportError:
    CursorAdapter = None

try:
    from .kiro_adapter import KiroAdapter
    register_agent('kiro', KiroAdapter)
except ImportError:
    KiroAdapter = None

try:
    from .autogpt_adapter import AutoGPTAdapter
    register_agent('autogpt', AutoGPTAdapter)
except ImportError:
    AutoGPTAdapter = None

# Optional Docker sandbox
try:
    from .sandbox import DockerSandbox
except ImportError:
    DockerSandbox = None

__all__ = [
    'BaseAgent',
    'AgentResult',
    'AgentStatus',
    'ToolCall',
    'get_agent',
    'register_agent',
    'list_agents',
    'AgentError',
    'temporary_workspace',
    'AiderAdapter',
]
