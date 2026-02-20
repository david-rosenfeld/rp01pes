# Closed-Source Agent Evaluation Package

## Overview

This document specifies the design for a **preliminary** manual evaluation of closed-source agentic coding assistants that lack programmatic APIs. The goal is to assess feasibility and gather initial comparative data to determine if a full study is warranted.

**Target Agents:**
- Cursor (IDE with AI agent)
- Amazon Kiro (IDE with AI agent)

**Scope:** Preliminary feasibility study (not publication-ready research)

**Design Goal:** Determine whether manual evaluation is practical and whether agents show meaningful differences worth investigating in a full study.

---

## Preliminary Study Scope

| Aspect | Full Study | This Preliminary Study |
|--------|------------|------------------------|
| Trials per task-agent | 10 | 3 |
| Total sessions | 100 | 30 |
| Counterbalancing | Latin Square | Simple alternation |
| Pilot study | Formal (4 sessions, κ > 0.8) | Informal (1 session) |
| Video recording | Required | Not required |
| Statistical analysis | Hypothesis tests | Descriptive only |
| Estimated effort | 10+ hours | 3-4 hours |

---

## Package Structure

```
closed_agent_eval/
├── README.md                    # Quick-start instructions
├── tasks/                       # Benchmark task definitions
│   ├── task_01_factorial/
│   │   ├── PROMPT.txt           # Exact prompt to paste
│   │   ├── initial/
│   │   │   └── math_utils.py
│   │   └── validate.py          # Validation script
│   ├── task_02_bugfix/
│   ├── task_03_test_generation/
│   ├── task_04_refactor/
│   └── task_05_documentation/
├── results/
│   ├── cursor/
│   └── kiro/
├── scripts/
│   ├── setup_workspace.py
│   ├── validate_result.py
│   └── summarize_results.py
└── instructions/
    ├── CURSOR_GUIDE.md
    └── KIRO_GUIDE.md
```

---

## Experimental Design

### Design Type

**Simple within-subjects comparison**
- Each task performed by both agents
- 3 trials per task-agent combination
- Alternate agents between sessions to reduce order effects

### Variables

**Independent:** Agent (Cursor vs Kiro)

**Dependent:**
- Task success (binary)
- Duration (seconds)
- Iteration count (approximate)
- User interventions required

### Trial Schedule

30 total sessions organized as:

| Session | Agent | Tasks |
|---------|-------|-------|
| 1 | Cursor | T1, T2, T3, T4, T5 |
| 2 | Kiro | T1, T2, T3, T4, T5 |
| 3 | Cursor | T1, T2, T3, T4, T5 |
| 4 | Kiro | T1, T2, T3, T4, T5 |
| 5 | Cursor | T1, T2, T3, T4, T5 |
| 6 | Kiro | T1, T2, T3, T4, T5 |

---

## Operational Definitions

### Iteration

Count as ONE iteration when the agent:
1. Produces visible output (text or code)
2. Performs an action (file edit, terminal command)
3. Shows "thinking" indicator for >2 seconds then produces output

### Task Completion

Task is complete when:
1. Agent explicitly states completion, OR
2. Agent inactive for 30 seconds, OR
3. 5-minute timeout reached

### Success

Task succeeds if ALL validation checks pass.

---

## Benchmark Tasks

Five tasks covering distinct coding activities:

| Task | Type | Purpose |
|------|------|---------|
| task_01_factorial | Feature Addition | Basic generation |
| task_02_bugfix | Bug Fix | Comprehension + fix |
| task_03_test_generation | Test Writing | Code understanding |
| task_04_refactor | Refactoring | Code transformation |
| task_05_documentation | Documentation | Non-functional output |

---

### Task 01: Add Factorial Function

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

**Success Criteria:**
- Function `factorial` exists
- `factorial(0) == 1`
- `factorial(5) == 120`
- `factorial(-1)` raises `ValueError`
- File is syntactically valid
- Existing functions still work

---

### Task 02: Fix Off-By-One Bug

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

**Prompt (`PROMPT.txt`):**
```
There is a bug in the paginate function. When requesting page 1 with a list [1,2,3,4,5] and per_page=2, it should return items [1, 2] but currently returns incorrect items.

Fix the bug so that:
- paginate([1,2,3,4,5], page=1, per_page=2) returns items [1, 2]
- paginate([1,2,3,4,5], page=2, per_page=2) returns items [3, 4]
- paginate([1,2,3,4,5], page=3, per_page=2) returns items [5]
```

**Success Criteria:**
- Page 1 returns `[1, 2]`
- Page 2 returns `[3, 4]`
- Page 3 returns `[5]`
- File is syntactically valid

---

### Task 03: Generate Unit Tests

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
- `test_validator.py` exists
- File is syntactically valid
- Contains at least 9 test functions
- `pytest` passes

---

### Task 04: Extract Function Refactoring

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
- Helper function exists (more than 2 functions total)
- `generate_sales_report` produces same output as reference
- `generate_inventory_report` produces same output as reference
- File is syntactically valid

---

### Task 05: Add Documentation

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
- Module has docstring
- Class has docstring
- All public methods have docstrings
- File is syntactically valid
- Class still functions correctly

---

## Result Recording

Record results in a simple JSON format:

```json
{
  "trial_id": "cursor_task01_001",
  "agent": "cursor",
  "task": "task_01_factorial",
  "trial_number": 1,
  "success": true,
  "duration_seconds": 45,
  "iterations": 3,
  "user_interventions": 0,
  "timeout": false,
  "notes": ""
}
```

Save each result to `results/<agent>/<trial_id>.json`.

---

## Execution Protocol

### Before Starting

1. Document agent versions (Cursor version, Kiro version)
2. Run 1 informal practice session with each agent to familiarize yourself with the process
3. Prepare workspace setup script

### Per-Session Procedure

1. **Setup:** Run `python scripts/setup_workspace.py --task <task_id>`
2. **Clear agent:** Start fresh conversation/session
3. **Open file:** Open target file in agent IDE
4. **Copy prompt:** Copy exact text from `PROMPT.txt`
5. **Start timer**
6. **Paste and submit**
7. **Observe:** Count iterations, note any issues
8. **Stop timer** when task completes
9. **Validate:** Run `python scripts/validate_result.py --task <task_id>`
10. **Record:** Save result JSON
11. **Reset:** Clean workspace for next trial

### Intervention Rules

**Allowed (count and document):**
- Confirming which file to edit
- Providing yes/no answers to agent questions

**Not allowed (invalidates trial):**
- Writing or suggesting code
- Explaining the bug or solution
- Providing hints

---

## Analysis Plan

For this preliminary study, use **descriptive statistics only**:

1. **Success rates** per agent per task
2. **Mean duration** per agent per task
3. **Mean iterations** per agent per task
4. **Intervention frequency**

Report as simple tables:

| Task | Cursor Success | Kiro Success | Cursor Avg Time | Kiro Avg Time |
|------|----------------|--------------|-----------------|---------------|
| factorial | 3/3 | 2/3 | 42s | 55s |
| ... | ... | ... | ... | ... |

### Decision Criteria

**Proceed to full study if:**
- Manual evaluation is practical (sessions complete without major issues)
- At least one agent succeeds on majority of tasks
- Observable differences suggest meaningful comparison is possible

**Do not proceed if:**
- Manual evaluation is impractical (too slow, unreliable, or frustrating)
- Both agents fail consistently
- Results are too variable to interpret

---

## Checklist Before Starting

- [ ] Agent versions documented
- [ ] Task files created in `tasks/` directories
- [ ] Validation scripts tested
- [ ] 1 practice session completed with each agent
- [ ] 3-4 hours blocked for main sessions
- [ ] Result recording template ready

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-20 | Initial design |
| 2.0 | 2026-02-20 | Major revision: Added rigor (Latin Square, pilot, etc.) |
| 3.0 | 2026-02-20 | Simplified for preliminary study scope |
