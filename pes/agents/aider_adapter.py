"""Aider agent adapter."""

import subprocess
import re
from pathlib import Path
from typing import Dict, Any

from .base import BaseAgent, AgentResult, AgentStatus


class AiderAdapter(BaseAgent):
    """
    Adapter for Aider (https://aider.chat).

    Aider is invoked via CLI with --message flag for non-interactive mode.

    Configuration:
        aider_path: Path to aider executable (default: "aider")
        model: Backend model (e.g., "gpt-4", "claude-3-opus")
    """

    def _validate_config(self) -> None:
        """Validate Aider configuration."""
        self.aider_path = self.config.get('aider_path', 'aider')

        # Verify aider is installed
        try:
            subprocess.run(
                [self.aider_path, '--version'],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise ValueError(f"Aider not found at {self.aider_path}") from e

    def _execute_task(
        self,
        task_prompt: str,
        files: Dict[str, str],
        **kwargs
    ) -> AgentResult:
        """Execute task using Aider."""
        # Build command
        cmd = [
            self.aider_path,
            '--yes',  # Auto-confirm
            '--no-git',  # Don't use git
            '--message', task_prompt,
        ]

        # Add model if specified
        if self.backend_model:
            cmd.extend(['--model', self.backend_model])

        # Add files
        for filename in files.keys():
            cmd.append(str(self.workspace / filename))

        # Execute
        result = subprocess.run(
            cmd,
            cwd=self.workspace,
            capture_output=True,
            text=True,
            timeout=self.timeout
        )

        # Determine modified files
        modified_files = self._get_modified_files(files)

        # Parse token usage from stderr (Aider outputs this)
        tokens = self._parse_token_usage(result.stderr)

        return AgentResult(
            status=AgentStatus.SUCCESS if result.returncode == 0 else AgentStatus.FAILED,
            success=result.returncode == 0,
            output=result.stdout,
            files_modified=modified_files,
            iterations=1,  # Aider does single-pass
            tool_calls=self._tool_calls,
            total_tokens=tokens.get('total', 0),
            prompt_tokens=tokens.get('prompt', 0),
            completion_tokens=tokens.get('completion', 0),
            duration_seconds=0.0,
            metadata={'stderr': result.stderr}
        )

    def _parse_token_usage(self, stderr: str) -> Dict[str, int]:
        """
        Parse token usage from Aider stderr output.

        Aider outputs lines like:
        "Tokens: 1,234 sent, 567 received. Cost: $0.02"
        """
        tokens = {'total': 0, 'prompt': 0, 'completion': 0}

        # Pattern for Aider token output
        pattern = r'Tokens:\s*([\d,]+)\s*sent,\s*([\d,]+)\s*received'
        match = re.search(pattern, stderr)

        if match:
            tokens['prompt'] = int(match.group(1).replace(',', ''))
            tokens['completion'] = int(match.group(2).replace(',', ''))
            tokens['total'] = tokens['prompt'] + tokens['completion']

        return tokens

    def _get_modified_files(self, original_files: Dict[str, str]) -> list:
        """Determine which files were modified."""
        modified = []
        for filename, original_content in original_files.items():
            filepath = self.workspace / filename
            if filepath.exists():
                current_content = filepath.read_text()
                if current_content != original_content:
                    modified.append(filename)
        return modified
