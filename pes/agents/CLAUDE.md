# CLAUDE.md - Agentic System Integration

## Scope

Adapters for agentic coding systems (Claude Code, Cursor, Aider, etc.).

## Status

**TODO** - Not yet implemented.

Required for: PE03 (Agent Selection)

## Planned Architecture

```
BaseAgent (abstract)
├── CLIAgentAdapter    # Command-line agents
├── APIAgentAdapter    # API-based agents
└── SandboxedAgent     # Isolated execution
```

## Requirements Reference

See REQ-3.3 (Agentic System Integration):
- REQ-3.3.1: Agent Abstraction Interface
- REQ-3.3.2: Agent Adapters
- REQ-3.3.3: Agent Capabilities
- REQ-3.3.4: Sandbox Environment

## Implementation Guidelines

When implementing:

1. Abstract interface similar to `BaseLLMProvider`
2. Agents operate on filesystem, not just prompts
3. Capture: iterations, tool calls, success rate
4. Sandbox isolation required (Docker or similar)
5. Resource limits (time, tokens, file access)
6. Telemetry collection for analysis

## Security Considerations

- Agents execute code; sandbox is mandatory
- Limit filesystem access to workspace
- Limit network access
- Set execution timeouts
- Log all tool invocations
