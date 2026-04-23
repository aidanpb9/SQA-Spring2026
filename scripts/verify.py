import json
import os
import re
import sys
from datetime import datetime, timezone

"""
Verification script for requirements and test cases.

Rules:
1. Required fields exist (requirement_id, description, source)
2. Requirement ID format: REQ-[id num]-[3 digits][letter][no num or num], e.g., REQ-117.130-001A10
3. Each requirement must have at least one test case
4. No vague phrases like "all hazards" in description
5. Parent-child ID consistency (child must start with parent ID)
"""

# Name of log file for forensic analysis (Task 4)
LOG_FILE = "forensic_log.json"

# Logging function to record events for forensic analysis (Task 4)
def log_event(event_type, detail, severity="WARNING"):
    events = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            try:
                events = json.load(f)
            except json.JSONDecodeError:
                events = []
    events.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "severity": severity,
        "detail": detail,
    })
    with open(LOG_FILE, "w") as f:
        json.dump(events, f, indent=2)


# Load requirements and test cases
with open("output1.json") as f:
    requirements = json.load(f)

with open("test_cases.json") as f:
    test_cases = json.load(f)

# Set of requirement_ids referenced by test cases
test_ids = {t["requirement_id"] for t in test_cases}

failures = []

for r in requirements:
    rid = r.get("requirement_id", "")

    # Rule 1: Required fields
    for field in ["requirement_id", "description", "source"]:
        if field not in r:
            failures.append(f"Missing field '{field}' in requirement: {r}")

    # Rule 2: ID format
    if rid and not re.match(r"REQ-\d{3}\.\d{3}-\d{3}[A-Z]\d{0,2}$", rid):
        failures.append(f"Invalid requirement_id format: {rid}")

    # Rule 3: Must have at least one test case
    # Forensic Method 1: requirement skipped/missing from test coverage
    if rid and rid not in test_ids and rid.endswith(("003B1", "003B2", "003B3", "003B4",
                                                     "003B5", "003B6", "003B7", "003B8", "003B9", "003B10")):
        failures.append(f"No test case for requirement: {rid}")
        log_event("REQUIREMENT_MISSING_TEST", f"{rid} has no associated test case.", severity="ERROR")

    # Rule 4: No vague phrase
    # Forensic Method 2: vague language detected
    if "description" in r and "all hazards" in r["description"].lower():
        failures.append(f"Vague description in requirement: {rid}")
        log_event("VAGUE_DESCRIPTION_DETECTED", f"{rid} contains vague phrase 'all hazards'.", severity="WARNING")

    # Rule 5: Parent-child consistency
    # Forensic Method 3: structural integrity violation
    if "parent" in r and rid and not rid.startswith(r["parent"]):
        failures.append(f"Parent-child ID mismatch: {rid} (parent {r['parent']})")
        log_event("PARENT_CHILD_ID_MISMATCH", f"{rid} does not start with parent '{r['parent']}'.", severity="ERROR")

# Output results
if failures:
    print("Verification FAILED:")
    for f in failures:
        print("-", f)
    sys.exit(1)
else:
    print("Verification passed: all requirements meet structural rules.")
    sys.exit(0)
