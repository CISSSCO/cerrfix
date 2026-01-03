import yaml
from pydantic import ValidationError
from schema.fix_schema import Fix

def load_and_validate_fix(path: str) -> Fix:
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        return Fix(**data)

    except FileNotFoundError:
        raise RuntimeError(f"Fix file not found: {path}")

    except ValidationError as e:
        raise RuntimeError(f"Schema validation failed:\n{e}")

