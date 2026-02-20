# Closed-Source Agent Evaluation Package

## Overview

This document specifies the design for a manual evaluation package enabling controlled PE03 (Agent Selection) experiments with closed-source agentic coding assistants that lack programmatic APIs.

**Target Agents:**
- Cursor (IDE with AI agent)
- Amazon Kiro (IDE with AI agent)

**Design Goal:** Enable repeatable, controlled experiments with minimal manual input while capturing the same telemetry as programmatic agent adapters.

---

## Threats to Validity and Mitigation Strategies

Before detailing the protocol, we identify key threats to internal and external validity:

| Threat | Type | Mitigation |
|--------|------|------------|
| Evaluator learning effects | Internal | Pilot trials (discarded); randomized task order |
| Evaluator bias toward agent | Internal | Single-blind where possible; standardized prompts |
| Agent context contamination | Internal | Fresh session per trial; clear conversation history |
| Task order effects | Internal | Latin Square counterbalancing design |
| Environmental variation | Internal | Controlled environment checklist; same time-of-day blocks |
| Network/API latency | Internal | Record and report; exclude outliers >2 SD |
| Inconsistent iteration counting | Internal | Operationalized definitions; pilot calibration |
| Small sample size | Statistical | Power analysis justification; effect size reporting |
| Prompt delivery variation | Internal | Clipboard paste only; no manual typing |
| Version drift | External | Pin and document all software versions |

---

## Package Structure

```
closed_agent_eval/
├── README.md                    # Quick-start instructions
├── PROTOCOL.md                  # Detailed experimental protocol
├── tasks/                       # Benchmark task definitions
│   ├── task_01_factorial/       # Task 1: Add factorial function
│   │   ├── PROMPT.txt           # Exact prompt to paste (plain text)
│   │   ├── initial/             # Initial workspace files
│   │   │   └── math_utils.py
│   │   ├── validation/          # Validation scripts (not visible during eval)
│   │   │   └── validate.py
│   │   └── SUCCESS_CRITERIA.md  # Operationalized success criteria
│   ├── task_02_bugfix/
│   ├── task_03_test_generation/
│   ├── task_04_refactor/
│   └── task_05_documentation/
├── results/
│   ├── schema.json              # JSON Schema for validation
│   ├── cursor/
│   └── kiro/
├── instructions/
│   ├── CURSOR_GUIDE.md
│   ├── KIRO_GUIDE.md
│   └── ENVIRONMENT_CHECKLIST.md # Pre-session environment verification
├── scripts/
│   ├── setup_workspace.py
│   ├── validate_result.py
│   ├── record_result.py
│   ├── generate_trial_order.py  # Latin Square randomization
│   ├── check_environment.py     # Environment verification
│   └── aggregate_results.py
├── pilot/                       # Pilot study materials
│   ├── pilot_tasks/             # Practice tasks (different from main)
│   └── pilot_results/           # Discarded pilot data
└── analysis/
    └── .gitkeep
```

**Important:** The `validation/` directories and `expected/` outputs must NOT be visible to the evaluator during task execution to prevent unconscious bias.

---

## Experimental Design

### Design Type

**Within-Subjects Repeated Measures Design**
- Each task is performed by both agents
- Multiple trials per task-agent combination
- Counterbalanced using Latin Square

### Independent Variables

| Variable | Levels | Notes |
|----------|--------|-------|
| Agent | Cursor, Kiro | Primary IV |
| Task | 5 benchmark tasks | Secondary IV |
| Backend Model | Varies by agent | Controlled, not manipulated |

### Dependent Variables

| Variable | Measurement | Operationalization |
|----------|-------------|-------------------|
| Task Success | Binary | All validation checks pass |
| Duration | Seconds | Prompt submission to final output |
| Iteration Count | Integer | See operational definition below |
| Tool Calls | Integer | Observable file/terminal operations |
| User Interventions | Integer | Any evaluator input after initial prompt |

### Sample Size Justification

**Target:** n = 10 trials per task-agent combination (100 total sessions)

**Rationale:**
- Detecting medium effect size (d = 0.5) for success rate differences
- With α = 0.05, power = 0.80, paired comparison
- Minimum n ≈ 8 per condition; using n = 10 for dropout buffer
- Pilot study (n = 2 per condition, discarded) to calibrate procedures

**Note:** If pilot reveals high variance, increase to n = 15.

---

## Operational Definitions

### Iteration (Critical Definition)

An **iteration** is defined as ONE of the following observable events:

1. **Agent produces visible output** (text response, code suggestion, explanation)
2. **Agent performs an action** (file edit, terminal command, file creation)
3. **Agent enters explicit "thinking" state** (visible thinking indicator for >2 seconds)

**NOT counted as iterations:**
- Typing indicators or loading spinners
- UI refreshes without content change
- Evaluator actions

**Calibration:** During pilot, two trials will be video-recorded and iteration counts independently verified.

### Task Completion

A task is **complete** when:
1. Agent explicitly states completion ("Done", "I've finished", etc.), OR
2. Agent stops producing output for 30 consecutive seconds, OR
3. 5-minute timeout is reached

### Success

A task is **successful** if and only if:
- ALL automated validation checks pass (see per-task criteria)
- No syntax errors in modified files
- Original functionality preserved (where applicable)

**Partial success is recorded as FAILURE** for primary analysis, but noted in metadata for secondary analysis.

---

## Benchmark Tasks

### Task Selection Rationale

Five tasks selected to cover distinct coding activities while minimizing confounds:

| Task | Type | Complexity | Est. Duration | Purpose |
|------|------|------------|---------------|---------|
| task_01_factorial | Feature Addition | Simple | 30-60s | Baseline generation |
| task_02_bugfix | Bug Fix | Simple | 30-90s | Comprehension + fix |
| task_03_test_generation | Test Writing | Medium | 60-120s | Code understanding |
| task_04_refactor | Refactoring | Medium | 60-180s | Code transformation |
| task_05_documentation | Documentation | Simple | 30-90s | Non-functional output |

**Note:** Estimated durations are for planning only; actual durations are measured.

---

### Task 01: Add Factorial Function

**Purpose:** Test basic code generation capability.

**Initial File (`initial/math_utils.py`):**
```python
"""Math utility functions."""


def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b
```

**Prompt (`PROMPT.txt`):**
```
Add a factorial function to this file. The function should:
1. Be named `factorial`
2. Take a single integer parameter `n`
3. Return the factorial of n (n!)
4. Handle edge cases: factorial(0) = 1, raise ValueError for negative inputs
5. Include a docstring following the existing style
```

**Success Criteria (Operationalized):**

| # | Criterion | Validation Method | Required |
|---|-----------|-------------------|----------|
| 1 | Function `factorial` exists | `hasattr(module, 'factorial')` | Yes |
| 2 | Accepts single parameter | `inspect.signature` check | Yes |
| 3 | `factorial(0) == 1` | Assert | Yes |
| 4 | `factorial(5) == 120` | Assert | Yes |
| 5 | `factorial(1) == 1` | Assert | Yes |
| 6 | `factorial(-1)` raises `ValueError` | `pytest.raises` | Yes |
| 7 | Function has non-empty docstring | `factorial.__doc__` truthy | Yes |
| 8 | File is syntactically valid | `py_compile.compile` | Yes |
| 9 | `add` function still works | `add(2,3) == 5` | Yes |
| 10 | `multiply` function still works | `multiply(2,3) == 6` | Yes |

**Success = ALL criteria pass**

---

### Task 02: Fix Off-By-One Bug

**Purpose:** Test debugging and code comprehension.

**Initial File (`initial/pagination.py`):**
```python
"""Pagination utilities."""


def paginate(items: list, page: int, per_page: int = 10) -> dict:
    """
    Paginate a list of items.

    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        per_page: Items per page

    Returns:
        Dict with 'items', 'page', 'total_pages', 'has_next', 'has_prev'
    """
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page

    start = page * per_page
    end = start + per_page

    page_items = items[start:end]

    return {
        'items': page_items,
        'page': page,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }
```

**Note:** The comment "# BUG:" has been intentionally removed to avoid cueing the solution.

**Prompt (`PROMPT.txt`):**
```
There is a bug in the paginate function. When requesting page 1 with a list [1,2,3,4,5] and per_page=2, it should return items [1, 2] but currently returns incorrect items.

Fix the bug so that:
- paginate([1,2,3,4,5], page=1, per_page=2) returns items [1, 2]
- paginate([1,2,3,4,5], page=2, per_page=2) returns items [3, 4]
- paginate([1,2,3,4,5], page=3, per_page=2) returns items [5]
```

**Success Criteria:**

| # | Criterion | Validation Method | Required |
|---|-----------|-------------------|----------|
| 1 | Page 1 returns `[1, 2]` | Assert items equality | Yes |
| 2 | Page 2 returns `[3, 4]` | Assert items equality | Yes |
| 3 | Page 3 returns `[5]` | Assert items equality | Yes |
| 4 | `has_next` correct for page 1 | Assert `True` | Yes |
| 5 | `has_prev` correct for page 1 | Assert `False` | Yes |
| 6 | File is syntactically valid | `py_compile.compile` | Yes |

---

### Task 03: Generate Unit Tests

**Purpose:** Test code understanding and test generation.

**Initial File (`initial/validator.py`):**
```python
"""Input validation utilities."""

import re


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate US phone number format (XXX-XXX-XXXX)."""
    pattern = r'^\d{3}-\d{3}-\d{4}$'
    return bool(re.match(pattern, phone))


def validate_password(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain an uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain a lowercase letter")
    if not re.search(r'\d', password):
        errors.append("Password must contain a digit")

    return len(errors) == 0, errors
```

**Prompt (`PROMPT.txt`):**
```
Create a test file `test_validator.py` using pytest. Include tests for all three functions:
1. validate_email - test valid emails, invalid emails, and edge cases
2. validate_phone - test valid formats and invalid formats
3. validate_password - test each validation rule individually and in combination

Include at least 3 test cases for each function.
```

**Success Criteria:**

| # | Criterion | Validation Method | Required |
|---|-----------|-------------------|----------|
| 1 | `test_validator.py` exists | File exists check | Yes |
| 2 | File is syntactically valid | `py_compile.compile` | Yes |
| 3 | Contains `test_` functions | AST parse count ≥ 9 | Yes |
| 4 | Tests pass | `pytest` exit code 0 | Yes |
| 5 | Tests actually test validator | Import check in tests | Yes |

---

### Task 04: Extract Function Refactoring

**Purpose:** Test refactoring capability.

**Initial File (`initial/report_generator.py`):**
```python
"""Report generation module."""


def generate_sales_report(sales_data: list[dict]) -> str:
    """Generate a sales report."""
    lines = []
    lines.append("=" * 50)
    lines.append("SALES REPORT")
    lines.append("=" * 50)
    lines.append("")

    total = 0
    for sale in sales_data:
        lines.append(f"  {sale['product']}: ${sale['amount']:.2f}")
        total += sale['amount']

    lines.append("")
    lines.append("-" * 50)
    lines.append(f"  TOTAL: ${total:.2f}")
    lines.append("=" * 50)

    return "\n".join(lines)


def generate_inventory_report(inventory_data: list[dict]) -> str:
    """Generate an inventory report."""
    lines = []
    lines.append("=" * 50)
    lines.append("INVENTORY REPORT")
    lines.append("=" * 50)
    lines.append("")

    total_items = 0
    for item in inventory_data:
        lines.append(f"  {item['name']}: {item['quantity']} units")
        total_items += item['quantity']

    lines.append("")
    lines.append("-" * 50)
    lines.append(f"  TOTAL ITEMS: {total_items}")
    lines.append("=" * 50)

    return "\n".join(lines)
```

**Prompt (`PROMPT.txt`):**
```
Refactor this code to reduce duplication. Extract common report formatting logic into a helper function that both generate_sales_report and generate_inventory_report can use.

Requirements:
- Create a helper function for the common formatting pattern
- Both original functions must produce identical output as before
- The external API (function signatures) must remain unchanged
```

**Success Criteria:**

| # | Criterion | Validation Method | Required |
|---|-----------|-------------------|----------|
| 1 | Helper function exists | Count functions > 2 | Yes |
| 2 | `generate_sales_report` produces same output | String comparison with reference | Yes |
| 3 | `generate_inventory_report` produces same output | String comparison with reference | Yes |
| 4 | Line count reduced by ≥ 5 lines | `wc -l` comparison | Yes |
| 5 | File is syntactically valid | `py_compile.compile` | Yes |
| 6 | No duplicate string literals for borders | AST analysis | Yes |

**Reference outputs for validation must be pre-generated from original file.**

---

### Task 05: Add Documentation

**Purpose:** Test documentation generation.

**Initial File (`initial/cache.py`):**
```python
from typing import Any, Optional
from datetime import datetime, timedelta
from threading import Lock


class TTLCache:
    def __init__(self, default_ttl: int = 300):
        self._cache = {}
        self._lock = Lock()
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                return None
            value, expiry = self._cache[key]
            if datetime.now() > expiry:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            expiry = datetime.now() + timedelta(seconds=ttl or self._default_ttl)
            self._cache[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
```

**Prompt (`PROMPT.txt`):**
```
Add documentation to this cache module:
1. Add a module-level docstring explaining what this module provides
2. Add a class docstring for TTLCache explaining its purpose and usage
3. Add docstrings for all public methods (get, set, delete, clear)
4. Use Google-style docstring format with Args, Returns, and Raises sections where applicable
```

**Success Criteria:**

| # | Criterion | Validation Method | Required |
|---|-----------|-------------------|----------|
| 1 | Module has docstring | `cache.__doc__` is truthy | Yes |
| 2 | Class has docstring | `TTLCache.__doc__` is truthy | Yes |
| 3 | `get` has docstring with Args/Returns | Parse docstring | Yes |
| 4 | `set` has docstring with Args | Parse docstring | Yes |
| 5 | `delete` has docstring with Args/Returns | Parse docstring | Yes |
| 6 | `clear` has docstring | `clear.__doc__` truthy | Yes |
| 7 | File is syntactically valid | `py_compile.compile` | Yes |
| 8 | Class still functions correctly | Basic usage test | Yes |

---

## Result Recording

### Result Schema (`results/schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["metadata", "task", "timing", "execution", "validation", "environment"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["evaluator_id", "date_iso", "agent", "agent_version", "backend_model", "trial_id"],
      "properties": {
        "evaluator_id": {"type": "string", "description": "Anonymized evaluator identifier"},
        "date_iso": {"type": "string", "format": "date-time"},
        "agent": {"type": "string", "enum": ["cursor", "kiro"]},
        "agent_version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+"},
        "backend_model": {"type": "string"},
        "trial_id": {"type": "string", "pattern": "^[a-z]+_task[0-9]{2}_[0-9]{3}$"}
      }
    },
    "task": {
      "type": "object",
      "required": ["task_id", "trial_number", "order_in_session"],
      "properties": {
        "task_id": {"type": "string"},
        "trial_number": {"type": "integer", "minimum": 1, "maximum": 15},
        "order_in_session": {"type": "integer", "minimum": 1, "maximum": 5}
      }
    },
    "timing": {
      "type": "object",
      "required": ["start_time_iso", "end_time_iso", "duration_seconds"],
      "properties": {
        "start_time_iso": {"type": "string", "format": "date-time"},
        "end_time_iso": {"type": "string", "format": "date-time"},
        "duration_seconds": {"type": "number", "minimum": 0},
        "timeout_reached": {"type": "boolean", "default": false}
      }
    },
    "execution": {
      "type": "object",
      "required": ["success", "iterations", "user_interventions"],
      "properties": {
        "success": {"type": "boolean"},
        "partial_success": {"type": "boolean", "description": "Some but not all criteria met"},
        "iterations": {"type": "integer", "minimum": 0},
        "user_interventions": {"type": "integer", "minimum": 0},
        "intervention_descriptions": {"type": "array", "items": {"type": "string"}},
        "tool_calls_observed": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "tool_type": {"type": "string", "enum": ["file_read", "file_write", "terminal", "search", "other"]},
              "description": {"type": "string"}
            }
          }
        },
        "files_modified": {"type": "array", "items": {"type": "string"}},
        "files_created": {"type": "array", "items": {"type": "string"}},
        "errors_observed": {"type": "array", "items": {"type": "string"}},
        "completion_signal": {"type": "string", "enum": ["explicit_statement", "inactivity_timeout", "time_timeout", "error"]}
      }
    },
    "validation": {
      "type": "object",
      "required": ["automated_check_passed", "criteria_results"],
      "properties": {
        "automated_check_passed": {"type": "boolean"},
        "criteria_results": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "criterion_id": {"type": "integer"},
              "passed": {"type": "boolean"},
              "error_message": {"type": "string"}
            }
          }
        },
        "validation_output": {"type": "string"}
      }
    },
    "environment": {
      "type": "object",
      "required": ["os", "python_version"],
      "properties": {
        "os": {"type": "string"},
        "python_version": {"type": "string"},
        "network_type": {"type": "string", "enum": ["wired", "wifi", "unknown"]},
        "time_of_day": {"type": "string", "enum": ["morning", "afternoon", "evening"]}
      }
    },
    "notes": {"type": "string"}
  }
}
```

---

## Counterbalancing Design

### Latin Square for Task Order

To control for task order effects, use a Latin Square design:

**For 5 tasks, 5 possible orderings (rows):**

| Session | Task 1 | Task 2 | Task 3 | Task 4 | Task 5 |
|---------|--------|--------|--------|--------|--------|
| Order A | T1 | T2 | T3 | T4 | T5 |
| Order B | T2 | T3 | T4 | T5 | T1 |
| Order C | T3 | T4 | T5 | T1 | T2 |
| Order D | T4 | T5 | T1 | T2 | T3 |
| Order E | T5 | T1 | T2 | T3 | T4 |

**Assignment:**
- Trials 1-2: Order A
- Trials 3-4: Order B
- Trials 5-6: Order C
- Trials 7-8: Order D
- Trials 9-10: Order E

**Agent Alternation:**
- Odd trials: Cursor first, then Kiro
- Even trials: Kiro first, then Cursor

### Trial Order Generation Script

```python
#!/usr/bin/env python3
"""Generate randomized trial order using Latin Square design."""

import json
import random
from pathlib import Path
from datetime import datetime

TASKS = ['task_01_factorial', 'task_02_bugfix', 'task_03_test_generation',
         'task_04_refactor', 'task_05_documentation']

LATIN_SQUARE = [
    [0, 1, 2, 3, 4],
    [1, 2, 3, 4, 0],
    [2, 3, 4, 0, 1],
    [3, 4, 0, 1, 2],
    [4, 0, 1, 2, 3],
]

def generate_trial_schedule(n_trials: int = 10, seed: int = None) -> list:
    """Generate complete trial schedule."""
    if seed:
        random.seed(seed)

    schedule = []
    trial_num = 1

    for trial_pair in range(n_trials // 2):
        # Determine Latin Square row
        ls_row = trial_pair % 5
        task_order = [TASKS[i] for i in LATIN_SQUARE[ls_row]]

        # Alternate agent order
        if trial_pair % 2 == 0:
            agents = ['cursor', 'kiro']
        else:
            agents = ['kiro', 'cursor']

        for agent in agents:
            for order_idx, task in enumerate(task_order):
                schedule.append({
                    'trial_id': f"{agent}_{task.split('_')[1]}_{trial_num:03d}",
                    'trial_number': trial_num,
                    'agent': agent,
                    'task': task,
                    'order_in_session': order_idx + 1,
                    'latin_square_row': chr(65 + ls_row)
                })
            trial_num += 1

    return schedule


def main():
    seed = int(datetime.now().timestamp())
    schedule = generate_trial_schedule(n_trials=10, seed=seed)

    output = {
        'generated': datetime.now().isoformat(),
        'seed': seed,
        'total_sessions': len(schedule) // 5,
        'schedule': schedule
    }

    output_path = Path(__file__).parent.parent / 'trial_schedule.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Generated schedule with seed {seed}")
    print(f"Total sessions: {len(schedule) // 5}")
    print(f"Saved to: {output_path}")


if __name__ == '__main__':
    main()
```

---

## Experimental Protocol

### Phase 1: Pilot Study (REQUIRED)

**Purpose:** Calibrate procedures and identify issues before main study.

**Pilot Protocol:**
1. Run 2 complete sessions per agent (4 total) using pilot tasks (NOT main tasks)
2. Video record at least 1 session per agent
3. Have second researcher independently count iterations from video
4. Calculate inter-rater reliability (require κ > 0.8)
5. Identify any procedural ambiguities
6. Adjust operational definitions if needed
7. **Discard all pilot data** - do not include in analysis

**Pilot Tasks:** Use simplified versions or entirely different tasks to avoid practice effects on main tasks.

### Phase 2: Environment Setup

**Environment Checklist (must verify EACH session):**

```markdown
## Pre-Session Environment Verification

Date: _____________ Session #: _____________

### Hardware
- [ ] Same physical machine as previous sessions
- [ ] External displays disconnected (or same configuration)
- [ ] Wired network connection (or documented WiFi)
- [ ] No other resource-intensive applications running

### Software
- [ ] Agent version matches: Cursor _______ / Kiro _______
- [ ] Python version: _______
- [ ] pytest version: _______
- [ ] OS: _______

### Agent State
- [ ] Fresh agent session started (no prior context)
- [ ] Conversation history cleared
- [ ] No files open in workspace
- [ ] Settings reset to default (or documented configuration)

### Evaluator State
- [ ] Reviewed operational definitions
- [ ] Timer/stopwatch ready
- [ ] Recording template open
- [ ] Break taken if fatigued

Verified by: _________________________ Time: _____________
```

### Phase 3: Main Study Execution

**Per-Session Procedure:**

1. **Verify environment** using checklist above
2. **Load trial schedule** and identify next trial
3. **Setup workspace:**
   ```bash
   python scripts/setup_workspace.py --task <task_id> --output ./workspace
   ```
4. **Clear agent state** (new conversation/session)
5. **Open target file** in agent IDE
6. **Prepare clipboard** - Copy exact text from `PROMPT.txt` (no modifications)
7. **Start timer** (use digital timer with milliseconds)
8. **Paste prompt** and submit
9. **Observe and count:**
   - Each iteration (per operational definition)
   - Tool calls (file reads, writes, terminal)
   - Any errors or unexpected behaviors
10. **Stop timer** when completion criterion met
11. **Run validation** (in separate terminal, NOT visible to agent):
    ```bash
    cd workspace && python ../scripts/validate_result.py --task <task_id>
    ```
12. **Record result** using `record_result.py` or manual entry
13. **Reset workspace** completely before next trial

### Timing Rules

| Event | Action |
|-------|--------|
| Prompt submitted | START timer |
| Agent says "done/finished/complete" | STOP timer |
| Agent inactive for 30 seconds | STOP timer |
| 5 minutes elapsed | STOP timer, mark timeout |
| Agent crashes/errors | STOP timer, record error |

### Intervention Protocol

**Level 0 - No intervention (preferred):**
- Agent works autonomously
- Record any confusion or errors without helping

**Level 1 - Permitted intervention (count and document):**
- Agent asks which file to edit → Point to file already open
- Agent asks for confirmation → Provide minimal yes/no
- Agent asks to clarify ambiguity IN the prompt → Re-read relevant prompt section only

**Level 2 - Prohibited (invalidates trial):**
- Writing or suggesting code
- Explaining what the bug is
- Providing hints beyond original prompt
- Correcting agent's approach

If Level 2 intervention occurs, mark trial as INVALID and repeat with fresh setup.

---

## Agent-Specific Instructions

### Cursor Configuration Requirements

```markdown
# Cursor Agent Evaluation - Configuration

## Required Settings
- Model: [Document exact model, e.g., "claude-3.5-sonnet"]
- Cursor version: [Exact version, e.g., "0.43.1"]
- Agent mode: Composer (not inline suggestions)

## Session Reset Procedure
1. Cmd+Shift+P → "Clear Chat History"
2. Close all open files
3. File → Close Folder
4. File → Open Folder → Select fresh workspace

## Prompt Submission
1. Open target file first
2. Cmd+K to open Composer
3. Paste prompt (do NOT type)
4. Press Enter to submit
5. Start timer immediately after Enter

## Iteration Counting for Cursor
Count as ONE iteration each time:
- Composer shows new text response
- Cursor makes a file edit (green/red diff appears)
- Cursor runs a terminal command
- Cursor shows "Thinking..." for >2 seconds then produces output
```

### Kiro Configuration Requirements

```markdown
# Kiro Agent Evaluation - Configuration

## Required Settings
- Backend: Claude Sonnet 4 (default, cannot change)
- Kiro version: [Document exact version]
- Mode: Agentic mode (not autocomplete)

## Session Reset Procedure
1. [Document exact Kiro reset procedure]
2. Clear any "specs" or planning documents
3. Close workspace and reopen fresh

## Prompt Submission
1. Open target file first
2. [Document exact Kiro invocation method]
3. Paste prompt (do NOT type)
4. Submit
5. Start timer immediately after submission

## Iteration Counting for Kiro
Count as ONE iteration each time:
- Kiro produces a response message
- Kiro creates or modifies a "spec" document
- Kiro makes a file edit
- Kiro runs a command
- Kiro shows extended thinking indicator then produces output
```

---

## Data Quality Checks

### Real-Time Checks (During Session)

- Trial ID matches schedule
- Timer started/stopped correctly
- Intervention level documented
- Completion signal identified

### Post-Session Checks

```python
def validate_session_data(result: dict) -> list[str]:
    """Return list of data quality warnings."""
    warnings = []

    # Timing sanity
    if result['timing']['duration_seconds'] < 5:
        warnings.append("Duration suspiciously short (<5s)")
    if result['timing']['duration_seconds'] > 300 and not result['timing']['timeout_reached']:
        warnings.append("Duration >5min without timeout flag")

    # Iteration sanity
    if result['execution']['iterations'] == 0 and result['execution']['success']:
        warnings.append("Success with 0 iterations is suspicious")
    if result['execution']['iterations'] > 50:
        warnings.append("Very high iteration count - verify counting")

    # Consistency
    if result['execution']['success'] and not result['validation']['automated_check_passed']:
        warnings.append("Manual success but automated check failed - investigate")

    return warnings
```

### Post-Study Checks

- All scheduled trials completed
- No duplicate trial IDs
- Version consistency across sessions
- Outlier analysis (flag trials >2 SD from mean duration)

---

## Analysis Plan

### Primary Analysis

1. **Success Rate Comparison**
   - McNemar's test for paired binary outcomes
   - Report exact success counts and percentages

2. **Duration Comparison**
   - Paired t-test or Wilcoxon signed-rank (depending on normality)
   - Report means, SDs, and effect sizes (Cohen's d)

3. **Iteration Comparison**
   - Same as duration

### Secondary Analysis

- Tool call patterns (descriptive)
- Intervention frequency by task
- Partial success analysis
- Timeout analysis

### Multiple Comparison Correction

With 5 tasks × 3 metrics = 15 comparisons:
- Apply Bonferroni correction (α = 0.05/15 = 0.0033)
- Or report uncorrected p-values with effect sizes for transparency

---

## Ethical Considerations

### Data Handling
- Evaluator IDs are anonymized
- No personal data in recordings
- Results stored securely

### Reproducibility
- All materials versioned in repository
- Trial schedule seed recorded for reproducibility
- Software versions documented

---

## Checklist Before Starting Main Study

- [ ] Pilot study completed (4 sessions, discarded)
- [ ] Inter-rater reliability verified (κ > 0.8 for iterations)
- [ ] Operational definitions finalized
- [ ] Environment checklist created
- [ ] Trial schedule generated and saved
- [ ] All task files created and tested
- [ ] Validation scripts tested on reference solutions
- [ ] Video recording capability confirmed (for verification)
- [ ] 8-10 hours blocked for main study sessions
- [ ] Backup procedure documented

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-20 | Initial design |
| 2.0 | 2026-02-20 | Major revision: Added threats to validity, operationalized definitions, Latin Square design, pilot study requirement, enhanced success criteria, data quality checks, environment controls |
