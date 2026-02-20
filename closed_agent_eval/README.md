# Closed-Source Agent Evaluation Package

Preliminary manual evaluation of Cursor and Kiro for PE03 (Agent Selection).

## Quick Start

1. **Setup environment:**
   ```bash
   cd closed_agent_eval
   pip install pytest  # if not already installed
   ```

2. **Run informal practice session** with each agent (1 session each)

3. **Execute trials** following the schedule:
   - Sessions alternate: Cursor, Kiro, Cursor, Kiro, Cursor, Kiro
   - 5 tasks per session
   - 3 trials per task-agent (30 total sessions)

4. **For each trial:**
   ```bash
   # Setup workspace
   python scripts/setup_workspace.py --task task_01_factorial

   # ... run agent with prompt from tasks/task_01_factorial/PROMPT.txt ...

   # Validate result
   python scripts/validate_result.py --task task_01_factorial

   # Record result in results/<agent>/
   ```

5. **Summarize results:**
   ```bash
   python scripts/summarize_results.py
   ```

## Directory Structure

```
closed_agent_eval/
├── tasks/                  # Task definitions (prompts, initial files, validators)
├── results/                # Trial results (JSON files)
├── scripts/                # Automation scripts
├── instructions/           # Agent-specific guides
└── workspace/              # Active workspace (created by setup script)
```

## Documentation

- [CURSOR_GUIDE.md](instructions/CURSOR_GUIDE.md) - Cursor-specific procedures
- [KIRO_GUIDE.md](instructions/KIRO_GUIDE.md) - Kiro-specific procedures
- [CLOSED_AGENTS.md](../CLOSED_AGENTS.md) - Full experimental design

## Trial Schedule

| Session | Agent  | Tasks |
|---------|--------|-------|
| 1       | Cursor | T1-T5 |
| 2       | Kiro   | T1-T5 |
| 3       | Cursor | T1-T5 |
| 4       | Kiro   | T1-T5 |
| 5       | Cursor | T1-T5 |
| 6       | Kiro   | T1-T5 |

Total: 30 task executions (6 sessions x 5 tasks)
