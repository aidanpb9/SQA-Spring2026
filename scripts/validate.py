import json
import os
import sys
from datetime import datetime, timezone

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


# Load requirements and expected structure
with open("output1.json") as f:
    requirements = json.load(f)

with open("output2.json") as f:
    expected_structure = json.load(f)

# Build set of actual requirement IDs
actual_ids = {r["requirement_id"] for r in requirements}

failures = []

# Check all expected enumerations exist
# Forensic Method 4: requirement declared in expected structure but absent from requirements.json
for parent, suffixes in expected_structure.items():
    for s in suffixes:
        rid = f"{parent}{s}"
        if rid not in actual_ids:
            failures.append(f"Missing requirement: {rid}")
            log_event("MISSING_REQUIREMENT", f"Expected {rid} is absent from requirements.json.", severity="ERROR")

# Forensic Method 5 (another 5th Method in ci.yaml): check for extra/unexpected requirements
for rid in actual_ids:
    parent = rid[:11]
    if parent in expected_structure:
        suffix = rid[-1]
        if suffix not in expected_structure[parent]:
            failures.append(f"Unexpected requirement: {rid}")
            log_event("UNEXPECTED_REQUIREMENT", f"Found {rid} which is not in the expected structure.", severity="WARNING")

if failures:
    print("\n".join(failures))
    sys.exit(1)
else:
    print(" Validation passed: all enumerations complete.")
