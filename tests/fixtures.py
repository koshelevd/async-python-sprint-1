import json

import pytest

from models.response import YandexResponse
from models.result import Result


@pytest.fixture
def response():
    """Fixture for YandexResponse."""
    with open('tests/response_fixture.json') as f:
        data = json.load(f)
    return YandexResponse(**data)

@pytest.fixture
def result_fixture():
    """Fixture for Result."""
    with open('tests/result_fixture.json') as f:
        data = json.load(f)
    return [Result(**item) for item in data]
