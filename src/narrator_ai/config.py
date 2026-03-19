"""Configuration management for narrator-ai CLI.

Stores server URL and API key in ~/.narrator-ai/config.yaml
"""

import os
from pathlib import Path

import yaml

CONFIG_DIR = Path.home() / ".narrator-ai"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "server": "https://openapi.jieshuo.cn",
    "app_key": "",
    "timeout": 30,
}


def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "r") as f:
        data = yaml.safe_load(f) or {}
    return {**DEFAULT_CONFIG, **data}


def save_config(config: dict):
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    CONFIG_FILE.chmod(0o600)


def get_server() -> str:
    cfg = load_config()
    server = os.environ.get("NARRATOR_SERVER", cfg.get("server", ""))
    if not server:
        raise SystemExit(
            "Server not configured. Run: narrator-ai-cli config init"
        )
    return server.rstrip("/")


def get_app_key() -> str:
    cfg = load_config()
    key = os.environ.get("NARRATOR_APP_KEY", cfg.get("app_key", ""))
    if not key:
        raise SystemExit(
            "API key not configured. Run: narrator-ai-cli config init"
        )
    return key


def get_timeout() -> int:
    cfg = load_config()
    return int(os.environ.get("NARRATOR_TIMEOUT", cfg.get("timeout", 30)))
