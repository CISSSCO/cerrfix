#!/usr/bin/env python3

from pathlib import Path
import re
import yaml
import os
from collections import Counter

from utils.paths import FIX_DIR
from utils.validation import load_and_validate_fix

from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()


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
        if "error_signature" not in fix:
            continue

        pattern = fix["error_signature"]["pattern"]

        try:
            compiled = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            console.print(
                f"[red]⚠ Invalid regex in {fix['issue_id']}:[/red] {e}"
            )
            continue

        if compiled.search(log):
            return fix
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


def stats():
    category_counter = Counter()
    severity_counter = Counter()
    total = 0
    invalid = 0

    for fix_file in FIX_DIR.glob("*.yaml"):
        try:
            fix = load_and_validate_fix(fix_file)
        except Exception as e:
            # print the names of the files if validation failed
            console.print(f"[red]Invalid fix:[/red] {fix_file.name} → {e}")
            invalid += 1
            continue

        total += 1
        category_counter[fix.category or "unknown"] += 1
        severity_counter[fix.severity or "unknown"] += 1

    console.print("\n[bold cyan]cerrfix fix statistics[/bold cyan]")
    console.print("-" * 35)

    summary = Text()
    summary.append("Total fixes : ", style="bold")
    summary.append(str(total), style="green")
    if invalid:
        summary.append(" | Invalid fixes : ", style="bold")
        summary.append(str(invalid), style="red")
    console.print(summary)
    console.print()

    table_cat = Table(title="By Category", header_style="bold magenta")
    table_cat.add_column("Category", style="cyan")
    table_cat.add_column("Count", justify="right", style="green")

    for cat, count in category_counter.most_common():
        table_cat.add_row(cat, str(count))

    console.print(table_cat)

    table_sev = Table(title="By Severity", header_style="bold magenta")
    table_sev.add_column("Severity", style="yellow")
    table_sev.add_column("Count", justify="right", style="green")

    for sev, count in severity_counter.most_common():
        table_sev.add_row(sev, str(count))

    console.print(table_sev)
    console.print()

def load_fix_by_id(issue_id: str):
    fix_file = FIX_DIR / f"{issue_id}.yaml"

    if not fix_file.exists():
        return None

    with open(fix_file) as f:
        return yaml.safe_load(f)

