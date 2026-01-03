#!/usr/bin/env python3
from pathlib import Path
import re
import yaml
import os

FIX_DIR = Path(__file__).parent / "fixes"

def load_fixes():
    fixes = []
    for fix_file in FIX_DIR.glob("*.yaml"):
        with open(fix_file) as f:
            fixes.append(yaml.safe_load(f))
    return fixes


def diagnose_log(logfile: Path):
    if not logfile.exists():
        raise FileNotFoundError(logfile)

    log = logfile.read_text()
    fixes = load_fixes()

    for fix in fixes:
        #pattern = fix["error_signature"]["pattern"]
        if "error_signature" not in fix:
            continue
        pattern = fix["error_signature"]["pattern"]


        try:
            if re.search(pattern, log, re.IGNORECASE):
                return fix
        except re.error as e:
            raise RuntimeError(
                f"Invalid regex in {fix['issue_id']}: {e}"
            )

    return None


def generate_fix_script(fix: dict, output_dir: Path):
    issue_id = fix["issue_id"]
    script_name = output_dir / f"fix_{issue_id}.sh"

    with open(script_name, "w") as sh:
        sh.write("#!/bin/bash\n\n")
        for step in fix["resolution"]["steps"]:
            sh.write(step + "\n")

    os.chmod(script_name, 0o755)
    return script_name
