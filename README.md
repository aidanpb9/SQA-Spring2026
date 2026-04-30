# NASA-SQA2026-AUBURN
## Verification and Validation of FDA Regulatory Requirements (21 CFR 117.130)

**Team:** Aidan Brinkley, Grant Carpenter, Blake Werk, Vincent Cameron
**Course:** COMP 5710 Software Quality Assurance Spring 2026
**GitHub Actions:** ![CI](https://github.com/aidanpb9/NASA-SQA2026-AUBURN/actions/workflows/ci.yaml/badge.svg)

---

## Project Objectives

This project applies Software Quality Assurance principles to a real regulatory document: 21 CFR 117.130 (FDA food safety hazard analysis requirements). The goals are to:

1. Parse a regulatory markdown document into structured, traceable requirements
2. Generate minimal test cases for selected atomic rules
3. Verify requirements meet structural rules and validate them against an expected structure
4. Integrate forensic event logging into the V&V pipeline and CI workflow to produce an auditable trail of failures

---

## Project Structure

```
NASA-SQA2026-AUBURN/
├── .github/
│   └── workflows/
│       └── ci.yaml              # GitHub Actions CI pipeline
├── scripts/
│   ├── verify.py                # Verification script (Task 3/4)
│   └── validate.py              # Validation script (Task 3/4)
├── CFR-117.130.md               # Input: CFR section in markdown format
├── generate_requirements.py     # Task 1: parse CFR into requirements JSON
├── generate_test_cases.py       # Task 2: generate test cases from requirements
├── output1.json                 # Generated requirements list
├── output2.json                 # Expected structure (parent -> children)
├── test_cases.json              # Generated test cases
├── forensic_log.json            # Forensic event log (written during V&V runs)
└── REPORT.md                    # Group project report
```

---

## Prerequisites

- **Python 3.10 or higher** (no third-party packages required, standard library only)
- Git

**Check your Python version:**

Mac/Linux:
```bash
python3 --version
```

Windows:
```cmd
python --version
```

---

## How to Reproduce Locally

> All commands must be run from the **project root** (`NASA-SQA2026-AUBURN/`). The scripts open files by relative path and will fail if run from a subdirectory.

### Clone the repository

Mac/Linux:
```bash
git clone https://github.com/aidanpb9/NASA-SQA2026-AUBURN.git
cd NASA-SQA2026-AUBURN
```

Windows:
```cmd
git clone https://github.com/aidanpb9/NASA-SQA2026-AUBURN.git
cd NASA-SQA2026-AUBURN
```

---

### Step 1 — Generate expected structure (Task 1)

> **Note on file naming:** The project specification refers to `requirements.json` and `expected_structure.json`. In this implementation, these correspond to `output1.json` and `output2.json` respectively. The content and role of each file is identical to what the spec describes. Only the names differ.
>
> `output1.json` serves as `requirements.json`: it is the full parsed list of atomic requirements extracted from `CFR-117.130.md`. It is committed directly to the repository because the script was modified during Task 1 to focus on generating the expected structure mapping, and the intermediate requirements list was preserved as a committed artifact. **It does not need to be regenerated.**
>
> Running the script below regenerates `output2.json`, which serves as `expected_structure.json`: a mapping of each parent requirement ID to its list of 10 selected child suffixes.

Mac/Linux:
```bash
python3 generate_requirements.py --input CFR-117.130.md --output output2.json --cfr "21 CFR 117.130"
```

Windows:
```cmd
python generate_requirements.py --input CFR-117.130.md --output output2.json --cfr "21 CFR 117.130"
```

Expected output:
```
Saved 10 requirements -> output2.json
```

---

### Step 2 — Generate test cases

Reads `output1.json` and `output2.json` and produces `test_cases.json` with one test case per selected requirement.

Mac/Linux:
```bash
python3 generate_test_cases.py
```

Windows:
```cmd
python generate_test_cases.py
```

Expected output:
```
test_cases.json generated successfully.
```

---

### Step 3 — Run verification

Checks 5 structural rules against all requirements and logs forensic events to `forensic_log.json` on any violation.

Mac/Linux:
```bash
python3 scripts/verify.py
```

Windows:
```cmd
python scripts\verify.py
```

Expected output (passing):
```
Verification passed: all requirements meet structural rules.
```

---

### Step 4 — Run validation

Checks that all expected requirements from `output2.json` are present in `output1.json` and logs forensic events for any missing or unexpected entries.

Mac/Linux:
```bash
python3 scripts/validate.py
```

Windows:
```cmd
python scripts\validate.py
```

Expected output (passing):
```
Validation passed: all enumerations complete.
```

---

## Forensic Logging

Both `verify.py` and `validate.py` write timestamped JSON events to `forensic_log.json` when a rule violation is detected. The CI workflow logs the overall build outcome (PASSED or FAILED) as a final forensic event and uploads the log as a downloadable artifact.

Six forensic event types are implemented:

| Event Type | Script | Trigger |
|---|---|---|
| `REQUIREMENT_MISSING_TEST` | verify.py | A required requirement has no test case |
| `VAGUE_DESCRIPTION_DETECTED` | verify.py | Description contains "all hazards" |
| `PARENT_CHILD_ID_MISMATCH` | verify.py | Child ID does not start with parent ID |
| `MISSING_REQUIREMENT` | validate.py | Expected requirement absent from output1.json |
| `UNEXPECTED_REQUIREMENT` | validate.py | Requirement not declared in expected structure |
| `CI_BUILD_STATUS` | ci.yaml | Final CI step logs PASSED or FAILED |

Example `forensic_log.json` entry:
```json
{
  "timestamp": "2026-04-23T21:50:06.858436+00:00",
  "event_type": "REQUIREMENT_MISSING_TEST",
  "severity": "ERROR",
  "detail": "REQ-117.130-003B3 has no associated test case."
}
```

The log remains empty (`[]`) when all checks pass.

---

## CI Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yaml`) runs automatically on every push and pull request. It executes Steps 3 and 4 above, logs the build outcome as a forensic event, and uploads `forensic_log.json` as a build artifact.

View CI run history: https://github.com/aidanpb9/NASA-SQA2026-AUBURN/actions
