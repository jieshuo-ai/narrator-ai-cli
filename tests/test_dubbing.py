"""Tests for narrator_ai.commands.dubbing — voice list filtering logic."""

import json

from typer.testing import CliRunner

from narrator_ai.commands.dubbing import DUBBING_LIST, app

runner = CliRunner()


def test_dubbing_list_not_empty():
    assert len(DUBBING_LIST) > 0


def test_dubbing_list_has_required_fields():
    for voice in DUBBING_LIST:
        assert "name" in voice
        assert "id" in voice
        assert "type" in voice
        assert "tag" in voice


def test_dubbing_list_json_output():
    result = runner.invoke(app, ["list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) > 0


def test_dubbing_list_filter_by_lang():
    result = runner.invoke(app, ["list", "--lang", "英语", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert all(v["type"] == "英语" for v in data)


def test_dubbing_list_filter_by_tag():
    result = runner.invoke(app, ["list", "--tag", "通用男声", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert all(v["tag"] == "通用男声" for v in data)


def test_dubbing_languages_json():
    result = runner.invoke(app, ["languages", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert any(item["language"] == "普通话" for item in data)


def test_dubbing_tags_json():
    result = runner.invoke(app, ["tags", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) > 0
