# HOW TO CONTINUE IN THE NEXT CONVERSATION

**This document explains exactly how to continue building the Preliminary Experiments System in future conversations with Claude.**

---

## Quick Start for Next Session

### Step 1: Upload Anchor Documents

At the start of your next conversation in this project, upload these three files:

1. **`ARCHITECTURE.md`** - System architecture and design decisions
2. **`IMPLEMENTATION_STATUS.md`** - What's done, what's TODO, and next steps
3. **`CONTINUATION_GUIDE.md`** - This file (optional, but helpful)

### Step 2: State Your Goal

Tell Claude what you want to work on. Examples:

> "I want to implement the OpenAI provider so PE02 works with real GPT-4."

> "I want to complete the PE04 (Temperature Optimization) experiment."

> "I want to add dataset loading for the LibEST dataset."

### Step 3: Claude Reads Context

Claude will:
1. Read the uploaded anchor documents
2. Use conversation_search to find relevant past discussions if needed
3. Understand where we left off
4. Propose an implementation plan

### Step 4: Build Incrementally

Work on one component at a time, testing as you go.

---

## Detailed Instructions for Common Scenarios

### Scenario 1: "I Want to Add a Real LLM Provider (OpenAI)"

**What to tell Claude:**

> "I want to implement the OpenAI provider for the LLM integration layer. I have my API key. Here are the anchor documents [upload ARCHITECTURE.md and IMPLEMENTATION_STATUS.md]."

**What Claude will do:**

1. Read the anchor documents to understand the BaseLLMProvider interface
2. Create `pes/llm/openai_provider.py` implementing the interface
3. Register it in `pes/llm/factory.py`
4. Update `configs/config.yaml` with OpenAI configuration
5. Show you how to test it with PE02

**What you need:**
- OpenAI API key
- Install: `pip install openai`

**Testing:**
```bash
# Update configs/config.yaml with your API key
# Change provider from "mock" to "openai" in PE02 config
python pe02.py configs/config.yaml
```

---

### Scenario 2: "I Want to Complete PE04 (Temperature Optimization)"

**What to tell Claude:**

> "I want to implement the Temperature Optimization experiment (PE04). I have the datasets and LLM providers working. Here are the anchor documents [upload]."

**What Claude will do:**

1. Read the anchor documents and PE04 stub code
2. Review REQ-3.6.4 from requirements
3. Look at PE02 as a reference pattern
4. Implement the full PE04 logic in `pes/experiments/pe04_temperatureoptimization.py`
5. Test with mock or real provider

**What you need:**
- LLM provider working (OpenAI, Anthropic, or mock)
- Task samples or ability to generate them
- Configuration for temperature ranges

---

### Scenario 3: "I Want to Add Dataset Loading"

**What to tell Claude:**

> "I want to implement dataset loading for the COMET datasets. I've downloaded them to ./data/. Here are the anchor documents [upload]."

**What Claude will do:**

1. Read the anchor documents
2. Review REQ-3.4 (Dataset Management) from requirements
3. Create the dataset module:
   - `pes/datasets/loader.py`
   - `pes/datasets/ground_truth.py`
   - `pes/datasets/traceability.py`
4. Test with one dataset (LibEST recommended)
5. Show how to use in experiments

**What you need:**
- COMET datasets downloaded to `data/` directory
- Know which dataset to test with first

---

### Scenario 4: "I Want to Add Statistical Analysis"

**What to tell Claude:**

> "I want to implement statistical analysis functions for experiments like PE01 and PE10. Here are the anchor documents [upload]."

**What Claude will do:**

1. Read the anchor documents
2. Review REQ-3.8.1 (Statistical Analysis) from requirements
3. Create `pes/analysis/statistics.py` with:
   - Descriptive statistics
   - Hypothesis tests (t-test, Wilcoxon)
   - Effect sizes (Cohen's d, Cliff's Delta)
   - Power analysis
4. Show usage examples

**What you need:**
- Install: `pip install numpy scipy`

---

### Scenario 5: "I Want to Generate Reports"

**What to tell Claude:**

> "I want to generate Markdown and HTML reports from experiment results. Here are the anchor documents [upload]."

**What Claude will do:**

1. Read the anchor documents
2. Review REQ-3.8.2-3.8.5 (Report Generation) from requirements
3. Create report generation modules
4. Add visualization support
5. Show how to generate reports from results

**What you need:**
- Install: `pip install matplotlib seaborn`
- For PDF: `pip install weasyprint`

---

## Using Past Chats Tools

Claude has built-in tools to search past conversations in this project. You don't need to do anything special - Claude can use these automatically when needed:

```python
# Claude can search past conversations
conversation_search(query="traceability bundle structure")

# Claude can retrieve recent chats
recent_chats(n=5)
```

**When Claude uses these:**
- When you reference "what we discussed earlier"
- When implementation details are needed from previous sessions
- When design decisions need to be recalled

**You don't need to worry about this** - just mention what you need and Claude will search if necessary.

---

## File Organization Tips

### Keep Your Work Organized

```
your_project/
├── pes/                    # System code (from Claude)
├── pe01.py - pe10.py       # Experiment programs (from Claude)
├── configs/                # Configuration files
├── data/                   # COMET datasets (you download)
├── logs/                   # Created at runtime
├── results/                # Created at runtime
├── ARCHITECTURE.md         # Upload to Claude
├── IMPLEMENTATION_STATUS.md  # Upload to Claude
├── CONTINUATION_GUIDE.md   # This file (optional)
└── requirements.txt        # Python dependencies
```

### After Each Session

1. **Update IMPLEMENTATION_STATUS.md** with what was completed
2. **Save all generated files** to your project directory
3. **Test the new code** before the next session
4. **Note any issues** to discuss next time

---

## Common Issues and Solutions

### Issue: "I can't find the anchor documents"

**Solution:** They're in the root directory of your project:
- `/path/to/project/ARCHITECTURE.md`
- `/path/to/project/IMPLEMENTATION_STATUS.md`

Look for them where you saved the Claude-generated files.

### Issue: "Claude doesn't remember our previous work"

**Solution:** 
1. Upload the anchor documents at the start of conversation
2. If that's not enough, tell Claude to search past chats:
   > "Search our previous conversation about the LLM provider interface"

### Issue: "The code doesn't work"

**Solution:**
1. Check that you have required dependencies installed
2. Check that config.yaml has correct paths and API keys
3. Check logs/ directory for error messages
4. Tell Claude the specific error message you're seeing

### Issue: "I don't know which component to build next"

**Solution:** Check IMPLEMENTATION_STATUS.md under "Next Steps" or ask Claude:
> "Based on my implementation status, what should I work on next? I want to prioritize components needed for experiment X."

---

## Best Practices for Multi-Session Development

### 1. Work Incrementally

Don't try to build everything at once. Instead:
- Session 1: Foundation (✅ Done)
- Session 2: One LLM provider
- Session 3: Dataset loading
- Session 4: One complete experiment
- And so on...

### 2. Test After Each Session

Before moving to the next component:
```bash
# Test what you just built
python pe02.py configs/config.yaml

# Check logs for issues
cat logs/*.log

# Verify results
cat results/*.json
```

### 3. Update Documentation

After each session:
- Update IMPLEMENTATION_STATUS.md with what's now complete
- Add notes about any issues or decisions
- Update ARCHITECTURE.md if design changed

### 4. Keep Code and Docs Together

Store everything in one directory:
- Makes it easy to find files
- Easy to upload to Claude
- Easy to version control with git

### 5. Use Version Control (Recommended)

```bash
git init
git add .
git commit -m "Session 1: Foundation complete"

# After each session:
git add .
git commit -m "Session 2: Added OpenAI provider"
```

This gives you:
- History of changes
- Ability to revert mistakes
- Clear progress tracking

---

## Template for Starting Next Session

Copy and paste this into your next conversation with Claude:

```
I'm continuing work on the Preliminary Experiments System. We last worked on 
[describe what was done in previous session].

I've uploaded ARCHITECTURE.md and IMPLEMENTATION_STATUS.md which document 
the current state of the system.

Today I want to work on: [describe your goal]

[If relevant: Here's the specific error I'm encountering...]
[If relevant: I have the following resources ready: API keys, datasets, etc.]

Please read the anchor documents and let me know your implementation plan.
```

---

## What If You Need to Start Over?

If you lose the files or need to recreate the system:

### Option 1: Use conversation_search

Tell Claude:
> "Search our past conversations about the Preliminary Experiments System foundation. I need to recreate the files."

### Option 2: Reference Past Chat URL

If you have the URL to the conversation where we created the system:
> "I need to recreate the system we built in [paste URL]. Can you search that conversation and regenerate the key files?"

### Option 3: Use This Guide

All the key design decisions are in ARCHITECTURE.md. Claude can recreate the foundation using that as a reference.

---

## Estimated Timeline for Complete System

Based on working 2-3 hours per session:

| Session | Goal | Time |
|---------|------|------|
| 1 (Done) | Foundation + PE02 | 3 hours |
| 2 | Real LLM providers | 2-3 hours |
| 3 | Dataset management | 3-4 hours |
| 4 | Complete PE01 | 2-3 hours |
| 5 | Complete PE04, PE07 | 3-4 hours |
| 6 | Complete PE10 | 2-3 hours |
| 7 | Statistical analysis | 2-3 hours |
| 8-10 | Remaining experiments | 6-9 hours |
| 11 | Report generation | 2-3 hours |
| 12 | Testing and polish | 2-3 hours |

**Total Estimate:** 30-40 hours across 12 sessions

You can adjust based on which experiments are highest priority.

---

## Quick Reference: Key Files

### Must Upload for Next Session
- `ARCHITECTURE.md` - System design
- `IMPLEMENTATION_STATUS.md` - What's done/TODO

### Core Code Files (Reference)
- `pes/core/base_experiment.py` - Pattern for all experiments
- `pes/llm/base.py` - Pattern for LLM providers
- `pes/experiments/pe02_model_selection.py` - Complete example

### Configuration
- `configs/config.yaml` - All settings

### Generated Each Run
- `logs/*.log` - Execution logs
- `results/*.json` - Experiment results

---

## Getting Help During Next Session

### If something is unclear:

> "Can you explain how the [component name] works based on the architecture document?"

### If you're stuck:

> "I'm trying to implement [X] but getting error [Y]. Can you help debug?"

### If you want to change the approach:

> "Looking at the current architecture, I think we should change [X] because [reason]. What do you think?"

### If you want to see an example:

> "Can you show me how to use the [component] based on how PE02 uses it?"

---

## Success Checklist for Each Session

Before ending a session, ensure:

- [ ] New code is saved to correct directory
- [ ] IMPLEMENTATION_STATUS.md is updated
- [ ] You've tested the new functionality
- [ ] Config files are updated if needed
- [ ] You know what to work on next
- [ ] Any issues are documented

---

## Final Tips

1. **Don't Rush** - Build incrementally, test thoroughly
2. **Ask Questions** - If unsure, ask Claude to explain
3. **Use Examples** - PE02 is your reference implementation
4. **Read Requirements** - `prelim_exp_requirements_md.md` has all details
5. **Test Early** - Don't wait until everything is built
6. **Document Decisions** - Add notes to ARCHITECTURE.md if design changes
7. **Have Fun** - This is research! Iterate and explore.

---

## Contact Info

If you have questions about this guide or the system:
1. Read ARCHITECTURE.md
2. Read IMPLEMENTATION_STATUS.md
3. Check the code comments
4. Ask Claude!

Good luck with your research! 🚀
