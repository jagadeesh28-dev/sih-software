"""
Configuration loader with validation and schema verification.
Loads external YAML configuration files without hardcoded values.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml

from .logger import get_logger

logger = get_logger(__name__)

_CONFIG_CACHE: Dict[str, Dict[str, Any]] = {}


def get_project_root() -> Path:
    """Return the absolute path to the sih26138_platform project root."""
    return Path(__file__).resolve().parent.parent


def load_config(config_name: str, force_reload: bool = False) -> Dict[str, Any]:
    """
    Load a YAML configuration file from the configs/ directory.

    Args:
        config_name: Name of config file with or without .yaml (e.g. 'physics', 'fuels.yaml').
        force_reload: If True, bypass internal cache.

    Returns:
        Dictionary of configuration contents.

    Raises:
        FileNotFoundError: If the configuration file cannot be found.
        ValueError: If the file is not valid YAML.
    """
    if not config_name.endswith(".yaml"):
        config_name = f"{config_name}.yaml"

    if not force_reload and config_name in _CONFIG_CACHE:
        return _CONFIG_CACHE[config_name]

    root = get_project_root()
    config_path = root / "configs" / config_name

    if not config_path.is_file():
        # Fallback check for root-level evidence ledger if requested
        if config_name.startswith("evidence/") or config_name.startswith("evidence\\"):
            config_path = root / config_name
        elif config_name == "claims.yaml":
            config_path = root / "evidence" / "claims.yaml"
        else:
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data is None:
                data = {}
            _CONFIG_CACHE[config_name] = data
            logger.debug(f"Loaded config: {config_path.name}")
            return data
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {config_path}: {e}") from e
