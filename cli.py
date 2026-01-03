#!/usr/bin/env python3
import typer
from pathlib import Path
from rich import print
import shutil

from utils.validation import load_and_validate_fix
from utils.paths import FIX_DIR
from core import diagnose_log, generate_fix_script, load_fixes

app = typer.Typer(
    name="cerrfix",
    help="cerrfix – diagnose and fix suggestion tool for Linux systems"
)

# ----------------------
# add-fix command
# ----------------------

@app.command("add-fix")
def add_fix(fix_file: Path):
    """
    Validate and add a fix YAML into the fix repository.
    """

    if not fix_file.exists():
        typer.secho("❌ Fix file not found.", fg=typer.colors.RED)
        raise typer.Exit(1)

    try:
        fix = load_and_validate_fix(str(fix_file))
    except RuntimeError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(1)

    filename = f"{fix.issue_id}.yaml"
    destination = FIX_DIR / filename

    if destination.exists():
        typer.secho(
            f"⚠️ Fix with issue_id '{fix.issue_id}' already exists.",
            fg=typer.colors.YELLOW
        )
        raise typer.Exit(1)

    shutil.copy(fix_file, destination)

    typer.secho(
        f"✅ Fix '{fix.issue_id}' added successfully.",
        fg=typer.colors.GREEN
    )


# ----------------------
# diagnose command
# ----------------------
@app.command()
def diagnose(
    logfile: Path = typer.Argument(..., exists=True, readable=True),
    generate: bool = typer.Option(True, "--generate/--no-generate",
                                  help="Generate fix shell script")
):
    """
    Diagnose an error log and suggest a fix.
    """

    fix = diagnose_log(logfile)

    if not fix:
        print("[red]❌ No known issue found[/red]")
        raise typer.Exit(code=1)

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
        print("\n[cyan]🛠 Fix script generated:[/cyan]")
        print(f"  source {script}")


# ----------------------
# list-fixes command
# ----------------------
@app.command("list-fixes")
def list_fixes():
    """
    List all available fixes.
    """
    fixes = load_fixes()

    for fix in fixes:
        print(
            f"- {fix['issue_id']} "
            f"[{fix.get('category', 'n/a')}] "
            f"{fix.get('title', '')}"
        )


# ----------------------
# search command
# ----------------------
@app.command()
def search(
    keyword: str = typer.Argument(...)
):
    """
    Search fixes by keyword.
    """
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


if __name__ == "__main__":
    app()
