"""Pytest fixtures."""

import importlib.util
import os
from pathlib import Path

import pytest


def _load_create_app():
    os.environ["SKIP_APP_AUTOCREATE"] = "1"
    app_file = Path(__file__).resolve().parent.parent / "app.py"
    spec = importlib.util.spec_from_file_location("simple_backend_app", app_file)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.create_app


@pytest.fixture()
def app():
    create_app = _load_create_app()
    test_app = create_app("sqlite+pysqlite:///:memory:", seed=True)
    test_app.config.update(TESTING=True)
    return test_app


@pytest.fixture()
def client(app):
    return app.test_client()
