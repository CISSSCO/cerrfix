#!/usr/bin/env python3
import typer
from pathlib import Path
from rich import print
import shutil
import yaml

from utils.validation import load_and_validate_fix
from utils.paths import FIX_DIR
from core import (
    diagnose_log,
    generate_fix_script,
    load_fixes,
    stats,
    load_fix_by_id,
)

app = typer.Typer(
    name="cerrfix",
    add_completion=False,  # 🔥 disables install/show completion
    help="""
cerrfix – diagnose and fix suggestion tool for Linux systems

Developer : Cisco Ramon
GitHub    : https://github.com/CISSSCO/

A rule-based expert system for identifying and suggesting
solutions to frequent problems encountered on Linux systems.
""",
    rich_markup_mode="rich",
)

# ----------------------
# add command
# ----------------------

@app.command("add")
def add_fix(fix_file: Path):
    """Validate and add a fix YAML into the fix repository."""
    if not fix_file.exists():
        typer.secho("❌ Fix file not found.", fg=typer.colors.RED)
        raise typer.Exit(1)

    try:
        fix = load_and_validate_fix(fix_file)
    except RuntimeError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(1)

    destination = FIX_DIR / f"{fix.issue_id}.yaml"

    if destination.exists():
        typer.secho(
            f"⚠️ Fix with issue_id '{fix.issue_id}' already exists.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(1)

    shutil.copy(fix_file, destination)
    typer.secho(
        f"✅ Fix '{fix.issue_id}' added successfully.",
        fg=typer.colors.GREEN,
    )

# ----------------------
# remove-fix command 
# ----------------------

@app.command("remove")
def remove_fix(
    issue_id: str = typer.Argument(..., help="Fix Issue ID to remove"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation"),
):
    """Remove an existing fix by issue ID."""
    fix_file = FIX_DIR / f"{issue_id}.yaml"

    if not fix_file.exists():
        print(f"[red]❌ Fix '{issue_id}' not found[/red]")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(
            f"⚠️ Are you sure you want to delete fix '{issue_id}'?"
        )
        if not confirm:
            print("[yellow]Aborted[/yellow]")
            raise typer.Exit(0)

    fix_file.unlink()
    print(f"[green]✅ Fix '{issue_id}' removed successfully[/green]")

# ----------------------
# update-fix command
# ----------------------

@app.command("update")
def update_fix(
    fix_file: Path = typer.Argument(..., help="Updated fix YAML file"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation"),
):
    """
    Update an existing fix using its issue_id.
    """
    if not fix_file.exists():
        typer.secho("❌ Fix file not found.", fg=typer.colors.RED)
        raise typer.Exit(1)

    try:
        fix = load_and_validate_fix(fix_file)
    except RuntimeError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(1)

    destination = FIX_DIR / f"{fix.issue_id}.yaml"

    if not destination.exists():
        typer.secho(
            f"❌ Fix '{fix.issue_id}' does not exist. Use add instead.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(
            f"⚠️ Update existing fix '{fix.issue_id}'?"
        )
        if not confirm:
            typer.secho("Aborted.", fg=typer.colors.YELLOW)
            raise typer.Exit(0)

    # Backup old fix
    backup = destination.with_suffix(".yaml.bak")
    shutil.copy(destination, backup)

    shutil.copy(fix_file, destination)

    typer.secho(
        f"✅ Fix '{fix.issue_id}' updated successfully.",
        fg=typer.colors.GREEN,
    )
    typer.secho(
        f"🗂 Backup created: {backup.name}",
        fg=typer.colors.BLUE,
    )


# ----------------------
# diagnose command
# ----------------------

@app.command()
def diagnose(
    logfile: Path = typer.Argument(..., exists=True, readable=True),
    generate: bool = typer.Option(True, "--generate/--no-generate"),
):
    """Diagnose an error log and suggest a fix."""
    fix = diagnose_log(logfile)

    if not fix:
        print("[red]❌ No known issue found[/red]")
        raise typer.Exit(1)

    print("\n[green]✅ Issue Detected![/green]")
    print(f"Issue ID    : {fix['issue_id']}")
    print(f"Description : {fix.get('title', 'N/A')}")
    print(f"Category    : {fix.get('category', 'unknown')}")
    print(f"Severity    : {fix.get('severity', 'unknown')}")

    print("\n[bold]🔧 Suggested Fix:[/bold]")
    for step in fix["resolution"]["steps"]:
        print(f"  $ {step}")

    if generate:
        script = generate_fix_script(fix, Path.cwd())
        print(f"\n[cyan]🛠 Run:[/cyan] source {script}")

# ----------------------
# list command
# ----------------------

@app.command("list")
def list_fixes():
    """List all available fixes."""
    fixes = load_fixes()
    for fix in fixes:
        print(f"[cyan]- {fix['issue_id']}[/cyan]\t{fix.get('title', '')}")

# ----------------------
# search command
# ----------------------

@app.command()
def search(keyword: str):
    """Search fixes by keyword."""
    fixes = load_fixes()
    keyword = keyword.lower()

    found = False
    for fix in fixes:
        haystack = (
            fix["issue_id"]
            + str(fix.get("title", ""))
            + str(fix.get("root_cause", ""))
        ).lower()

        if keyword in haystack:
            found = True
            print(f"- {fix['issue_id']} : {fix.get('title', '')}")

    if not found:
        print("[yellow]No matching fixes found[/yellow]")

# ----------------------
# stats command
# ----------------------

@app.command("stats")
def stats_cmd():
    """Show fix statistics"""
    stats()

# ----------------------
# show command
# ----------------------

@app.command()
def show(
    issue_id: str = typer.Argument(..., help="Fix Issue ID to display")
):
    """
    Show full details of a fix (raw YAML content).
    """
    fix = load_fix_by_id(issue_id)

    if not fix:
        print(f"[red]❌ Fix '{issue_id}' not found[/red]")
        raise typer.Exit(1)

    print("\n[bold green]✅ Fix Details[/bold green]\n")

    # Header summary
    print(f"[cyan]Issue ID[/cyan]    : {fix.get('issue_id')}")
    print(f"[cyan]Title[/cyan]       : {fix.get('title', 'N/A')}")
    print(f"[cyan]Category[/cyan]    : {fix.get('category', 'N/A')}")
    print(f"[cyan]Severity[/cyan]    : {fix.get('severity', 'N/A')}")
    print()

    # Error signature
    if "error_signature" in fix:
        print("[bold]🔍 Error Signature[/bold]")
        for k, v in fix["error_signature"].items():
            print(f"  {k}: {v}")
        print()

    # Resolution steps
    print("[bold]🔧 Resolution Steps[/bold]")
    for step in fix.get("resolution", {}).get("steps", []):
        print(f"  $ {step}")
    print()

    # Raw YAML output
    print("[bold]📄 Raw Fix YAML[/bold]")
    print(yaml.dump(fix, sort_keys=False))


if __name__ == "__main__":
    app()
