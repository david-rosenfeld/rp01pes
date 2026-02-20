# Cursor Agent Evaluation Guide

## Prerequisites

- Cursor IDE installed
- Document exact version: `Cursor > About Cursor`
- Note the backend model being used (e.g., Claude 3.5 Sonnet, GPT-4)

## Pre-Session Setup

1. **Verify Cursor version:** _____________
2. **Backend model:** _____________
3. **Close all other applications**

## Session Reset Procedure

Before EACH trial:

1. **Clear conversation history:**
   - Cmd+Shift+P (Mac) / Ctrl+Shift+P (Windows)
   - Type "Clear Chat History" and select it

2. **Close all files:**
   - Cmd+W repeatedly or File > Close All

3. **Close current folder:**
   - File > Close Folder

4. **Open fresh workspace:**
   - File > Open Folder
   - Select the `workspace` directory created by `setup_workspace.py`

## Prompt Submission Procedure

1. **Open the target file** in the editor

2. **Open Composer:**
   - Cmd+K (Mac) / Ctrl+K (Windows)
   - Or click the Composer button

3. **Paste the prompt:**
   - Copy exact text from `PROMPT.txt`
   - Paste into Composer (do NOT type manually)

4. **Start your timer**

5. **Press Enter** to submit

6. **Observe and count iterations**

## Iteration Counting for Cursor

Count as ONE iteration each time:

- Composer shows a new text response
- Cursor makes a file edit (green/red diff appears)
- Cursor runs a terminal command
- Cursor shows "Thinking..." for >2 seconds then produces output

Do NOT count:
- Loading spinners
- Typing indicators
- UI refreshes without content

## Completion Detection

Task is complete when:

1. Cursor explicitly states completion ("Done", "I've finished", etc.)
2. No new output for 30 seconds
3. 5-minute timeout reached

## Recording

After each trial:

1. Stop your timer
2. Note the duration
3. Note iteration count
4. Run validation script
5. Record result using `record_result.py`

## Troubleshooting

**Agent not responding:**
- Check internet connection
- Restart Cursor
- Mark trial as failed if issue persists

**Agent asks for clarification:**
- Provide minimal yes/no if permitted
- Count this as an intervention
- Do NOT provide hints or explanations
