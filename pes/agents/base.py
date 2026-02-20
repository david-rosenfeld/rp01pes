"""
Abstract base class for agentic system integration.

Implements REQ-3.3.1 (Agent Abstraction Interface).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import time


class AgentStatus(Enum):
    """Agent execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class ToolCall:
    """Record of a single tool invocation."""
    tool_name: str
    arguments: Dict[str, Any]
    result: Any
    timestamp: float
    duration_seconds: float


@dataclass
class AgentResult:
    """
    Standardized agent execution result.

    Captures all telemetry needed for PE03 analysis.
    """
    status: AgentStatus
    success: bool
    output: str
    files_modified: List[str]
    iterations: int
    tool_calls: List[ToolCall]
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    duration_seconds: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for agent adapters.

    All agent implementations must inherit from this class.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        workspace: Path,
        backend_model: Optional[str] = None
    ):
        """
        Initialize agent.

        Args:
            config: Agent configuration
            workspace: Path to isolated workspace directory
            backend_model: LLM model to use as backend
        """
        self.config = config
        self.workspace = workspace
        self.backend_model = backend_model
        self.timeout = config.get('timeout_seconds', 300)
        self.max_iterations = config.get('max_iterations', 20)

        # Telemetry tracking
        self._tool_calls: List[ToolCall] = []
        self._iterations = 0
        self._total_tokens = 0

        # Validate configuration
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate agent-specific configuration."""
        pass

    @abstractmethod
    def _execute_task(
        self,
        task_prompt: str,
        files: Dict[str, str],
        **kwargs
    ) -> AgentResult:
        """
        Execute a coding task.

        Args:
            task_prompt: Natural language task description
            files: Dict mapping filename -> content for initial workspace
            **kwargs: Additional task parameters

        Returns:
            AgentResult with execution telemetry
        """
        pass

    def run(
        self,
        task_prompt: str,
        files: Dict[str, str],
        **kwargs
    ) -> AgentResult:
        """
        Execute task with timing and error handling.

        This wraps _execute_task with common functionality.
        """
        start_time = time.time()

        try:
            # Set up workspace
            self._setup_workspace(files)

            # Execute task
            result = self._execute_task(task_prompt, files, **kwargs)

            # Record duration
            result.duration_seconds = time.time() - start_time

            return result

        except TimeoutError:
            return AgentResult(
                status=AgentStatus.TIMEOUT,
                success=False,
                output="",
                files_modified=[],
                iterations=self._iterations,
                tool_calls=self._tool_calls,
                total_tokens=self._total_tokens,
                prompt_tokens=0,
                completion_tokens=0,
                duration_seconds=time.time() - start_time,
                error="Execution timeout"
            )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                success=False,
                output="",
                files_modified=[],
                iterations=self._iterations,
                tool_calls=self._tool_calls,
                total_tokens=self._total_tokens,
                prompt_tokens=0,
                completion_tokens=0,
                duration_seconds=time.time() - start_time,
                error=str(e)
            )

    def _setup_workspace(self, files: Dict[str, str]) -> None:
        """Set up isolated workspace with provided files."""
        self.workspace.mkdir(parents=True, exist_ok=True)

        for filename, content in files.items():
            filepath = self.workspace / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content)

    def _record_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Any,
        duration: float
    ) -> None:
        """Record a tool invocation for telemetry."""
        self._tool_calls.append(ToolCall(
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            timestamp=time.time(),
            duration_seconds=duration
        ))
