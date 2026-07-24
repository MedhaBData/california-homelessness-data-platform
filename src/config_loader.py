from pathlib import Path

import yaml


CONFIG_FILE = Path("config/config.yaml")


def load_config():
    """
    Load configuration from config.yaml.
    """

    with open(CONFIG_FILE, "r") as file:
        return yaml.safe_load(file)