from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_google_auth_migration_depends_on_initial_schema() -> None:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    script = ScriptDirectory.from_config(config)

    baseline = script.get_revision("initial_schema")
    google_auth = script.get_revision("add_google_auth_columns")

    assert baseline is not None
    assert google_auth.down_revision == baseline.revision
