"""
Schema definitions and required field mappings for maritime time-series datasets.
Exposes canonical schema contract and field validators.
"""

from pathlib import Path
from typing import Any, Dict
import yaml

_SCHEMA_PATH = Path(__file__).resolve().parent / "canonical_schema.yaml"


def load_canonical_schema() -> Dict[str, Any]:
    """Load canonical schema contract from canonical_schema.yaml."""
    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CANONICAL_SCHEMA = load_canonical_schema()
REQUIRED_FIELDS = list(CANONICAL_SCHEMA["fields"].keys())
FIELD_DEFINITIONS = CANONICAL_SCHEMA["fields"]

# Aliases for backwards compatibility with initial Phase 0 skeleton
REQUIRED_VESSEL_FIELDS = REQUIRED_FIELDS
FIELD_UNITS = {k: v.get("physical_unit", "unknown") for k, v in FIELD_DEFINITIONS.items()}

__all__ = [
    "CANONICAL_SCHEMA",
    "REQUIRED_FIELDS",
    "FIELD_DEFINITIONS",
    "REQUIRED_VESSEL_FIELDS",
    "FIELD_UNITS",
    "load_canonical_schema",
]
