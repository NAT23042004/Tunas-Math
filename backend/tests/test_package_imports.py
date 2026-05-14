from fastapi import FastAPI

from toan_socratic.db.models import Base
from toan_socratic.main import app, create_app


def test_package_imports_expose_bootstrap_objects() -> None:
    assert isinstance(app, FastAPI)
    assert isinstance(create_app(), FastAPI)
    assert Base.metadata.tables
