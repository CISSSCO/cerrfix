#!/usr/bin/env python3

import re
import yaml
import sys
from pathlib import Path

FIX_DIR = Path("/home/abhi581b/git/cerrfix/fixes")

def load_fixes():
    fixes = []
    for fix_file in FIX_DIR.glob("*.yaml"):
        with open(fix_file) as f:
            fixes.append(yaml.safe_load(f))
    return fixes

def diagnose(logfile):
    with open(logfile) as f:
        log = f.read()

    fixes = load_fixes()

    for fix in fixes:
        pattern = fix["error_pattern"]

        try:
            if re.search(pattern, log, re.IGNORECASE):
                issue_id = fix["issue_id"]
                script_name = f"fix_{issue_id}.sh"

                print("\n✅ Issue Detected!")
                print(f"Issue ID    : {issue_id}")
                print(f"Description : {fix['description']}")
                print(f"Root Cause  : {fix['root_cause']}")
                print("\n🔧 Suggested Fix:")
                for step in fix["solution"]:
                    print(f"  $ {step}")

                # Create shell script
                with open(script_name, "w") as sh:
                    sh.write("#!/bin/bash\n\n")
                    for step in fix["solution"]:
                        sh.write(f"{step}\n")

                # Make script executable
                import os
                os.chmod(script_name, 0o755)

                print("\n🛠 Fix script generated:")
                print(f"  📄 {script_name}")
                print("\n▶️ To apply the fix, run:")
                print(f"  source ./{script_name}")

                return

        except re.error as e:
            print(f"⚠️ Invalid regex in {fix['issue_id']}: {e}")

    print("❌ No known issue found.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: cerrfix.py <logfile>")
        sys.exit(1)

    diagnose(sys.argv[1])
