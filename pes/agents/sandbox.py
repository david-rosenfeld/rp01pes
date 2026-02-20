"""
Sandboxed execution environment for agents.

Implements REQ-3.3.4 (Sandbox Environment).
"""

import tempfile
import shutil
from pathlib import Path
from contextlib import contextmanager
from typing import Generator, Dict


@contextmanager
def temporary_workspace() -> Generator[Path, None, None]:
    """
    Create a temporary isolated workspace.

    This is the REQUIRED minimum isolation level.

    Yields:
        Path to temporary directory

    The directory is automatically cleaned up on exit.
    """
    workspace = Path(tempfile.mkdtemp(prefix="pes_agent_"))
    try:
        yield workspace
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


# ---------------------------------------------------------------------
# OPTIONAL: Docker-based sandbox (requires docker package and Docker daemon)
# Only implement if stronger isolation is required for your use case.
# For initial implementation, temporary_workspace() is sufficient.
# ---------------------------------------------------------------------

try:
    import docker

    class DockerSandbox:
        """
        Docker-based sandbox for agent execution (OPTIONAL).

        Provides stronger isolation than filesystem-only sandboxing.
        Requires: pip install docker, Docker daemon running
        """

        def __init__(self, image: str = "python:3.11-slim"):
            self.image = image
            self.client = docker.from_env()

        def run(
            self,
            command: list,
            files: Dict[str, str],
            timeout: int = 300
        ) -> dict:
            """
            Run command in Docker container with provided files.
            """
            with temporary_workspace() as workspace:
                for filename, content in files.items():
                    (workspace / filename).write_text(content)

                container = self.client.containers.run(
                    self.image,
                    command=command,
                    volumes={str(workspace): {'bind': '/workspace', 'mode': 'rw'}},
                    working_dir='/workspace',
                    detach=True,
                    mem_limit='2g',
                    cpu_period=100000,
                    cpu_quota=50000,
                    network_mode='none'
                )

                try:
                    result = container.wait(timeout=timeout)
                    logs = container.logs()
                    return {
                        'exit_code': result['StatusCode'],
                        'stdout': logs.decode('utf-8'),
                        'stderr': ''
                    }
                finally:
                    container.remove(force=True)

except ImportError:
    # Docker not available - that's fine, it's optional
    DockerSandbox = None
