# Kiro Agent Evaluation Guide

## Prerequisites

- Amazon Kiro installed
- Document exact version
- Note: Kiro uses Claude Sonnet 4 as backend (not configurable)

## Pre-Session Setup

1. **Verify Kiro version:** _____________
2. **Backend model:** Claude Sonnet 4 (default)
3. **Close all other applications**

## Session Reset Procedure

Before EACH trial:

1. **Clear any existing context:**
   - Close all open conversations/chats
   - Clear any "specs" or planning documents

2. **Close current workspace:**
   - File > Close Folder (or equivalent)

3. **Open fresh workspace:**
   - File > Open Folder
   - Select the `workspace` directory created by `setup_workspace.py`

4. **Verify clean state:**
   - No files open
   - No previous conversation visible

## Prompt Submission Procedure

1. **Open the target file** in the editor

2. **Invoke Kiro agent:**
   - [Document exact method for your Kiro version]
   - Example: Cmd+Shift+K or click agent button

3. **Paste the prompt:**
   - Copy exact text from `PROMPT.txt`
   - Paste into agent input (do NOT type manually)

4. **Start your timer**

5. **Submit** (Enter or Send button)

6. **Observe and count iterations**

## Iteration Counting for Kiro

Count as ONE iteration each time:

- Kiro produces a response message
- Kiro creates or modifies a "spec" document
- Kiro makes a file edit
- Kiro runs a command in terminal
- Kiro shows extended thinking indicator then produces output

Do NOT count:
- Loading indicators
- UI updates without content change

## Completion Detection

Task is complete when:

1. Kiro explicitly states completion ("Done", "Finished", etc.)
2. No new output for 30 seconds
3. 5-minute timeout reached

## Kiro-Specific Notes

- Kiro may create "spec" files as part of its planning process
- Count spec creation as an iteration
- If Kiro asks to create a spec for a simple task, count any intervention

## Recording

After each trial:

1. Stop your timer
2. Note the duration
3. Note iteration count
4. Run validation script
5. Record result using `record_result.py`

## Troubleshooting

**Agent not responding:**
- Check AWS/Kiro connection status
- Restart Kiro
- Mark trial as failed if issue persists

**Agent asks for clarification:**
- Provide minimal yes/no if permitted
- Count this as an intervention
- Do NOT provide hints or explanations

## Version-Specific Instructions

[Fill in after installing and testing Kiro]

- Exact agent invocation method: _____________
- Chat/conversation location: _____________
- How to clear history: _____________
