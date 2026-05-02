from pathlib import Path


ENTRYPOINT = Path("docker/docker-entrypoint-nestjs.sh")


def _entrypoint_text() -> str:
    return ENTRYPOINT.read_text(encoding="utf-8")


def test_prisma_migrations_use_direct_url_then_restore_runtime_url() -> None:
    text = _entrypoint_text()

    assert "ORIGINAL_DATABASE_URL=${DATABASE_URL:-}" in text
    assert 'export DATABASE_URL="$DATABASE_URL_DIRECT"' in text
    assert 'export DATABASE_URL="$ORIGINAL_DATABASE_URL"' in text
    assert "unset DATABASE_URL_DIRECT" in text


def test_entrypoint_cleans_unfinished_prisma_migration_rows_before_deploy() -> None:
    text = _entrypoint_text()

    cleanup_pos = text.index("cleanup_unfinished_migrations")
    deploy_pos = text.index("run_migrations", cleanup_pos)
    assert cleanup_pos < deploy_pos
    assert 'UPDATE "_prisma_migrations"' in text
    assert "finished_at IS NULL AND rolled_back_at IS NULL" in text
    assert "rolled_back_at = COALESCE(rolled_back_at, NOW())" in text


def test_p3018_duplicate_object_detection_covers_postgres_sqlstates() -> None:
    text = _entrypoint_text()

    for pattern in ("42P06", "42P07", "42701", "42710"):
        assert pattern in text

    assert "relation .* already exists" in text
    assert "constraint .* already exists" in text
    assert "index .* already exists" in text
    assert "column .* already exists" in text


def test_p3018_migration_name_extraction_is_posix_compatible() -> None:
    text = _entrypoint_text()

    assert "grep -oP" not in text
    assert "sed -n 's/.*Migration name:" in text
