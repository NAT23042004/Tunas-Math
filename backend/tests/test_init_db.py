import pytest

from toan_socratic import init_db


@pytest.mark.asyncio
async def test_main_only_runs_seed_step(monkeypatch) -> None:
    called = {"seed": False}

    async def fail_if_schema_init_runs() -> None:
        raise AssertionError("schema initialization should be handled by Alembic")

    async def fake_load_sample_problems() -> None:
        called["seed"] = True

    monkeypatch.setattr(init_db, "init_database", fail_if_schema_init_runs, raising=False)
    monkeypatch.setattr(init_db, "load_sample_problems", fake_load_sample_problems)

    await init_db.main()

    assert called["seed"] is True
