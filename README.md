# Self-Healing Browser Agent

A Playwright-based browser automation prototype that detects selector failures, identifies alternative interaction targets, executes recovery actions, and verifies outcomes.

## Overview

Traditional browser automation scripts often fail when page elements change their IDs, labels, or loading behavior.

This project explores a recovery mechanism that can:
- Recover from changed element selectors.
- Identify buttons using accessible names.
- Wait for asynchronously loaded elements.
- Detect ambiguous targets and avoid unsafe clicks.
- Verify action outcomes instead of assuming execution succeeded.
- Record execution traces as JSON reports.

## Architecture

```text
Browser Page
     |
     v
Recovery Engine
     |
     v
Original Selector
     |
     v
Fallback Target Identification
     |
     v
Ambiguity Check
     |
     v
Recovery Action
     |
     v
Outcome Verification
     |
     v
Execution Trace
     |
     v
JSON Reports
     |
     v
Streamlit Analytics Dashboard
```

## Tech Stack

- Python 3.11
- Playwright
- Pytest
- Streamlit
- Pandas

## Project Structure

```text
self-healing-agent/
├── tests/
│   ├── test_execution_trace.py
│   └── test_recovery.py
├── .gitignore
├── test_page.html
├── dynamic_test_page.html
├── accessible_label_test_page.html
├── async_test_page.html
├── recovery_engine.py
├── execution_trace.py
└── dashboard.py
```

## Setup

Clone the repository:

```bash
git clone https://github.com/ejaz029/self-healing-browser-agent.git
cd self-healing-browser-agent
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install playwright pytest streamlit pandas
python -m playwright install chromium
```

## Run Tests

```bash
python -m pytest -v
```

**Current test result:** 11 passed.

## Run the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard displays execution history, recovery outcomes, success rates, and recovery strategy usage based on generated JSON reports.

## Current Scope and Limitations

- This is a local proof of concept using controlled HTML test pages.
- Recovery currently targets the specific `Confirm Order` button.
- Fallback identification uses Playwright accessible-name matching.
- Asynchronous element detection uses a fixed three-second waiting window.
- The prototype does not yet integrate with external browser-agent frameworks.
- Recovery success is verified against a specific expected page status.

## Future Direction

Explore integration with broader browser-agent workflows, configurable recovery policies, and more general target identification.

## Author

**Ejaz Belgaum**

GitHub: [ejaz029](https://github.com/ejaz029)
