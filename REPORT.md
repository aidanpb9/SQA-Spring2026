# SQA Spring 2026 — Group Project Report

## Team Members

Aidan Brinkley, Vincent Cameron, Grant Carpenter, Blake Werk

---

## Overview

This project applied Software Quality Assurance (SQA) principles to the document 21 CFR 117.130. We extracted structured requirements from the regulation, generated test cases, built verification and validation (V&V) scripts, and integrated forensic event logging into the CI/CD pipeline.

---

## Task 0: Project Repository

We created a GitHub repository (`aidanpb9/SQA-Spring2026`) and added all team members as collaborators. A GitHub Actions workflow (`.github/workflows/ci.yaml`) was created to run automatically on every push and pull request, executing both the verification and validation scripts as part of the CI pipeline.

---

## Task 1: Extract and Structure Requirements

**What we did:**

We used `generate_requirements.py` to parse `CFR-117.130.md` into a JSON file (`output1.json`). The script identified hierarchical sections and assigned requirement IDs in the format `REQ-117.130-[section][letter][number]` (such as `REQ-117.130-003B1`).

We selected 10 rules from section 003B (subsections B1–B10) and created `output2.json` mapping the parent requirement `REQ-117.130-003B` to its 10 child suffixes.

**Run command:**
```bash
python3 generate_requirements.py --input CFR-117.130.md --output output1.json --cfr "21 CFR 117.130"
```

**What we learned:**

Regulatory documents use deeply nested and inconsistent structures. Parsing them required careful handling of parent/child relationships and letter/number enumeration schemes. We learned that requirement ID design has a significant impact on traceability and downstream validation.

---

## Task 2: Generate Minimal Test Cases

**What we did:**

We wrote `generate_test_cases.py` to take in `output1.json` and `output2.json` and produce `test_cases.json`. This file has one minimal test case per selected requirement. Each test case includes:

- `test_case_id` (TC-001 through TC-010)
- `requirement_id`
- `description`
- `input_data`
- `expected_output`
- `steps`
- `notes`

**Run command:**
```bash
python3 generate_test_cases.py
```

**What we learned:**

Writing minimal test cases made us think about what each atomic rule actually requires as observable behavior. Even simple regulatory clauses can have non-obvious input/output boundaries when translated into testable conditions.

---

## Task 3: Verification and Validation

**What we did:**

We wrote two scripts in `scripts/`:

- **`verify.py`**: checks 5 structural rules against every requirement:
  1. Required fields present (`requirement_id`, `description`, `source`)
  2. Requirement ID matches expected format
  3. Each selected requirement has at least one test case
  4. No vague phrases (ex. "all hazards") in descriptions
  5. Child IDs must begin with their declared parent ID

- **`validate.py`**: checks completeness against `output2.json`:
  - Every expected child requirement exists in `output1.json`
  - No unexpected/undeclared requirements are present

Both scripts exit with code 1 on failure, integrating cleanly with GitHub Actions.

**Run commands:**
```bash
python3 scripts/verify.py
python3 scripts/validate.py
```

**Sample output (passing):**
```
Verification passed: all requirements meet structural rules.
Validation passed: all enumerations complete.
```

**What we learned:**

Separating verification (internal structural correctness) from validation (conformance to expected specification) is a meaningful distinction. Verification catches format and consistency issues; validation catches missing or extra requirements relative to the declared scope.

---

## Task 4: Forensic Integration

**What we did:**

We integrated forensic event logging directly into both V&V scripts. Each script defines a `log_event()` function that writes timestamped events in JSON to `forensic_log.json`. We implemented 6 forensic integration points, with one in the CI yaml script:

| Method | Location | Event Type | Trigger |
|--------|----------|-----------|---------|
| 1 | `scripts/verify.py` | `REQUIREMENT_MISSING_TEST` | A required requirement has no test case |
| 2 | `scripts/verify.py` | `VAGUE_DESCRIPTION_DETECTED` | Description contains "all hazards" |
| 3 | `scripts/verify.py` | `PARENT_CHILD_ID_MISMATCH` | Child ID does not start with parent ID |
| 4 | `scripts/validate.py` | `MISSING_REQUIREMENT` | Expected requirement absent from `output1.json` |
| 5 | `scripts/validate.py` | `UNEXPECTED_REQUIREMENT` | Requirement found that was not declared in expected structure |
| 6 | `.github/workflows/ci.yaml` | `CI_BUILD_STATUS` | Final CI step logs PASSED or FAILED build outcome |

The CI workflow uploads `forensic_log.json` as a build artifact on every run (including failures) using `actions/upload-artifact`.

**What we learned:**

Forensic logging transforms passive pass/fail outputs into an audit trail. Attaching severity levels (`INFO`, `WARNING`, `ERROR`) and timestamps to each event makes it possible to reconstruct exactly what went wrong, when it happened, and in which script, which is valuable for debugging CI failures in team environments.

---

## Forensic Execution Log

The following is a representative `forensic_log.json` output showing all 6 forensic event types firing (simulated failure scenario):

```json
[
  {
    "timestamp": "2026-04-23T21:50:06.858436+00:00",
    "event_type": "REQUIREMENT_MISSING_TEST",
    "severity": "ERROR",
    "detail": "REQ-117.130-003B3 has no associated test case."
  },
  {
    "timestamp": "2026-04-23T21:50:06.858899+00:00",
    "event_type": "VAGUE_DESCRIPTION_DETECTED",
    "severity": "WARNING",
    "detail": "REQ-117.130-001A contains vague phrase 'all hazards'."
  },
  {
    "timestamp": "2026-04-23T21:50:06.859046+00:00",
    "event_type": "PARENT_CHILD_ID_MISMATCH",
    "severity": "ERROR",
    "detail": "REQ-117.130-003B1 does not start with parent 'REQ-117.130-003'."
  },
  {
    "timestamp": "2026-04-23T21:50:06.859181+00:00",
    "event_type": "MISSING_REQUIREMENT",
    "severity": "ERROR",
    "detail": "Expected REQ-117.130-003B11 is absent from requirements.json."
  },
  {
    "timestamp": "2026-04-23T21:50:06.859334+00:00",
    "event_type": "UNEXPECTED_REQUIREMENT",
    "severity": "WARNING",
    "detail": "Found REQ-117.130-003C which is not in the expected structure."
  },
  {
    "timestamp": "2026-04-23T21:50:06.859454+00:00",
    "event_type": "CI_BUILD_STATUS",
    "severity": "ERROR",
    "detail": "CI build FAILED"
  }
]
```

**Normal passing run output:**
```
Verification passed: all requirements meet structural rules.
Validation passed: all enumerations complete.
```
_(forensic_log.json remains empty `[]` when all checks pass)_

---

## GitHub Actions CI Log

The CI workflow (`.github/workflows/ci.yaml`) runs automatically on every push and pull request. The pipeline:

1. Checks out the repository
2. Sets up Python 3.10
3. Runs `scripts/verify.py`
4. Runs `scripts/validate.py`
5. Logs CI build pass/fail status as a forensic event
6. Uploads `forensic_log.json` as a downloadable build artifact

To view GitHub Actions logs and download the forensic artifact:  
`https://github.com/aidanpb9/SQA-Spring2026/actions`

<img width="1470" height="917" alt="Screenshot 2026-04-24 at 1 38 23 PM" src="https://github.com/user-attachments/assets/d0bde575-5f84-44c8-97ea-c2c5754e26e9" />

---

## Summary of Lessons Learned

- **Regulatory documents require careful parsing.** Hierarchical numbering in CFR sections does not always map cleanly to parent/child structures in code.
- **Requirement IDs are a traceability backbone.** A consistent, parseable ID format makes verification, validation, and forensic logging significantly easier to implement and audit.
- **Verification ≠ Validation.** These are complementary but distinct checks — one tests internal consistency, the other tests conformance to a declared specification.
- **Forensic logging adds accountability.** A simple timestamped event log turns a CI pipeline from a binary pass/fail gate into an auditable record of what failed, why, and when.
- **CI integration closes the loop.** Running V&V automatically on every push ensures that regressions are caught immediately rather than discovered later in the development cycle.
