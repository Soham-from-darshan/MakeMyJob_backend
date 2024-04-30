import pytest
from instance import TestingConfiguration
from Application import create_app, db
from tests import nameValidationTestCases, passwordValidationTestCases
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
    with app.app_context():
        yield db

@pytest.fixture(params=[*nameValidationTestCases.items()])
def nameTestCase(request):
    return request.param

@pytest.fixture(params=[*passwordValidationTestCases.items()])
def passwordTestCase(request):
    return request.param