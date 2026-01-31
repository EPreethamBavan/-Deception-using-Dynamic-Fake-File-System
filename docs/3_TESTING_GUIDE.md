# MIRAGE Testing Guide

## Overview
This guide explains how to verify that the Deception Engine (MIRAGE) is working correctly. It is designed for the QA team and Junior Developers to validate the system before panel submission.

> [!NOTE]
> This guide covers both **Windows** (Local Development) and **Linux** (Server Deployment) instructions.

---

## Part 1: Setup & Prerequisities

### 1.1 Environment Setup
Before running tests, ensure you have Python installed and dependencies set up.

**Windows (PowerShell):**
```powershell
# Open the project folder
cd "Deception using Dynamic Fake File System"

# Create a virtual environment
python -m venv venv

# Activate the environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

**Linux / Mac:**
```bash
cd "Deception using Dynamic Fake File System"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 1.2 Configuration
Ensure you have a valid `.env` file in the `config/` directory or root.
It must contain your Gemini API key:
```ini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
```

---

## Part 2: Automated Unit Tests
The easiest way to verify the system is to run the automated test suite.

### Run All Tests
```bash
# Windows
python tests/run_all_tests.py

# Linux
python3 tests/run_all_tests.py
```

### Expected Output
You should see output similar to this:
```
test_proc_version_generation ... ok
test_detect_cowrie_fingerprint ... ok
test_add_command ... ok
...
----------------------------------------------------------------------
Ran 22 tests in 2.134s

OK
```
**If you see `FAILED`**: Check the error message. Common causes are missing API keys or missing dependencies.

---

## Part 3: Manual Verification (The "Living Machine" Check)

### 3.1 Dry Run Test (Safe Mode)
Run the engine in simulation mode to see what it *would* do without modifying your file system.

```bash
# Windows
python sys_core.py --dry-run --llm --strategy-hybrid

# Linux
python3 sys_core.py --dry-run --llm --strategy-hybrid
```
**Verify:**
1.  Logs appear in the console or `monitor_debug.log`.
2.  You see "Executing Scene" messages.
3.  Paths look realistic options (e.g., `C:\Users\Target\repos` on Windows or `/home/dev_alice` on Linux).

### 3.2 Anti-Fingerprinting Check
Verify that the system generates realistic "fake" system files (like `/proc/cpuinfo`) to fool attackers.

```bash
python tests/test_antifingerprint_manual.py
```
**Look for:**
- `HOSTFS` or `UML` signatures (Should be **ABSENT**).
- Realistic Kernel versions (Should be **PRESENT**).

### 3.3 LLM Connection Check
Verify the AI brain is reachable.

```bash
python tests/test_llm_connection.py
```
**Success:** Prints a generated command from the AI.
**Failure:** Prints connection errors (check your VPN or API Key).

---

## Part 4: "Living Machine" Validation
This is the most critical part for the panel. We need to prove the system creates its own environment.

1.  **Modify Configuration**: Open `config/worker-spec.json` and change a persona's probability to `1.0` (Always active).
2.  **Run Engine**: `python sys_core.py --llm --strategy-hybrid` (Run for 1-2 minutes then `Ctrl+C`).
3.  **Check Artifacts**:
    *   **History**: Check `.bash_history` files in the simulated home directories.
    *   **Context**: Ensure commands match the persona (e.g., Alice doing Dev work, Bob doing Admin work).
    *   **Paths**: Verify that if the LLM hallucinated a new project folder, it was created on disk.

---

## Part 5: Troubleshooting for Team

**Issue: "Module not found"**
*   **Fix**: Ensure your virtual environment is activated (`(venv)` should appear in your prompt).

**Issue: "403 Forbidden" / API Error**
*   **Fix**: Your API Key is invalid or expired. generated a new one in Google AI Studio.

**Issue: Paths look wrong on Windows**
*   **Note**: The system mimics Linux paths even on Windows for deception purposes, but maps them to valid local directories where possible. This is expected behavior.

---

### 3.4 Agentic Feature Verification (New)
Validate the PROACTIVE features (Defender Agent & Skills):

```bash
# Run with hybrid strategy
python sys_core.py --llm --strategy-hybrid --dry-run
```

**Look for in logs:**
1.  **Defender Decision:** `[Defender Agent] Decision: ...` (e.g., `SKILL`, `LIVE_LLM`).
2.  **Skill Execution:** `Skill Execution: Git` or `Skill Execution: Docker` in the scene description.
3.  **Memory Usage:** References to "Story Arc" or "Project State" in debug logs (if enabled).

---

## Final Checklist for Panel Submission
- [ ] All 22 Unit Tests PASS.
- [ ] Dry Run executes without crashing.
- [ ] `legacy_archive` folders are ignored/cleaned.
- [ ] `.env` file is NOT included in the final zip (security risk).
