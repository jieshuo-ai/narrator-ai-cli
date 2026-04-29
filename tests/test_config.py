"""Tests for narrator_ai.config module."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from narrator_ai.config import (
    DEFAULT_CONFIG,
    get_app_key,
    get_server,
    get_timeout,
    load_config,
    save_config,
)


def test_default_config_values():
    assert DEFAULT_CONFIG["server"] == "https://openapi.jieshuo.cn"
    assert DEFAULT_CONFIG["app_key"] == ""
    assert DEFAULT_CONFIG["timeout"] == 30


def test_load_config_returns_defaults_when_no_file(tmp_path):
    with patch("narrator_ai.config.CONFIG_FILE", tmp_path / "nonexistent.yaml"):
        cfg = load_config()
    assert cfg["server"] == DEFAULT_CONFIG["server"]
    assert cfg["timeout"] == DEFAULT_CONFIG["timeout"]


def test_save_and_load_config(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_dir = tmp_path
    with patch("narrator_ai.config.CONFIG_FILE", config_file), \
         patch("narrator_ai.config.CONFIG_DIR", config_dir):
        save_config({"server": "https://test.example.com", "app_key": "test-key"})
        cfg = load_config()
    assert cfg["server"] == "https://test.example.com"
    assert cfg["app_key"] == "test-key"
    assert cfg["timeout"] == 30  # default preserved


def test_get_server_from_env():
    with patch.dict(os.environ, {"NARRATOR_SERVER": "https://env.example.com"}):
        assert get_server() == "https://env.example.com"


def test_get_server_strips_trailing_slash():
    with patch.dict(os.environ, {"NARRATOR_SERVER": "https://example.com/"}):
        assert get_server() == "https://example.com"


def test_get_server_raises_when_not_configured(tmp_path):
    with patch("narrator_ai.config.CONFIG_FILE", tmp_path / "nonexistent.yaml"), \
         patch.dict(os.environ, {}, clear=True):
        # DEFAULT_CONFIG has server set, so this won't raise
        server = get_server()
        assert server == DEFAULT_CONFIG["server"].rstrip("/")


def test_get_app_key_from_env():
    with patch.dict(os.environ, {"NARRATOR_APP_KEY": "env-key-123"}):
        assert get_app_key() == "env-key-123"


def test_get_app_key_raises_when_not_configured(tmp_path):
    with patch("narrator_ai.config.CONFIG_FILE", tmp_path / "nonexistent.yaml"), \
         patch.dict(os.environ, {}, clear=True):
        with pytest.raises(SystemExit):
            get_app_key()


def test_get_timeout_from_env():
    with patch.dict(os.environ, {"NARRATOR_TIMEOUT": "60"}):
        assert get_timeout() == 60


def test_get_timeout_default():
    with patch.dict(os.environ, {}, clear=True), \
         patch("narrator_ai.config.CONFIG_FILE", Path("/nonexistent")):
        assert get_timeout() == 30
