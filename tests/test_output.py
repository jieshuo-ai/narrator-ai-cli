"""Tests for narrator_ai.output module."""

import json

from narrator_ai.output import print_error, print_info, print_json, print_success


def test_print_json_dict(capsys):
    print_json({"key": "value", "num": 42})
    out = json.loads(capsys.readouterr().out)
    assert out["key"] == "value"
    assert out["num"] == 42


def test_print_json_list(capsys):
    print_json([1, 2, 3])
    out = json.loads(capsys.readouterr().out)
    assert out == [1, 2, 3]


def test_print_json_unicode(capsys):
    print_json({"name": "测试"})
    out = json.loads(capsys.readouterr().out)
    assert out["name"] == "测试"


def test_print_error_with_code(capsys):
    print_error("something failed", code=404)
    err = capsys.readouterr().err
    assert "404" in err
    assert "something failed" in err


def test_print_error_without_code(capsys):
    print_error("generic error")
    err = capsys.readouterr().err
    assert "generic error" in err


def test_print_success(capsys):
    print_success("done!")
    err = capsys.readouterr().err
    assert "done!" in err


def test_print_info(capsys):
    print_info("processing...")
    err = capsys.readouterr().err
    assert "processing..." in err
