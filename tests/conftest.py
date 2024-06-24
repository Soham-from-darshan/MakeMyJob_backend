import pytest
from instance import TestingConfiguration
from Application import create_app, db
from flask import Flask

@pytest.fixture
def app() -> Flask:
    app = create_app(configClass=TestingConfiguration)
    return app

@pytest.fixture
def client(app: Flask):
    return app.test_client()

@pytest.fixture
def database(app):
    return db
