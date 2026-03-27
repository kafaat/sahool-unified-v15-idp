"""Test database migration SQL files are valid."""

import os
import re

import pytest

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "../../infrastructure/migrations")


class TestMigrationFiles:
    def test_migration_files_exist(self):
        assert os.path.isdir(MIGRATIONS_DIR), f"Migrations directory not found: {MIGRATIONS_DIR}"
        sql_files = [f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql")]
        assert len(sql_files) > 0, "No SQL migration files found"

    def test_migration_001_syntax(self):
        path = os.path.join(MIGRATIONS_DIR, "001_performance_indexes.sql")
        if not os.path.exists(path):
            pytest.skip("Migration 001 not found")
        with open(path) as f:
            content = f.read()
        assert "CREATE INDEX" in content
        assert "idx_fields_tenant_id" in content
        assert "idx_fields_geom" in content
        assert "GIST" in content  # PostGIS spatial index

    def test_migration_uses_concurrently(self):
        path = os.path.join(MIGRATIONS_DIR, "001_performance_indexes.sql")
        if not os.path.exists(path):
            pytest.skip("Migration 001 not found")
        with open(path) as f:
            content = f.read()
        # Most indexes should use CONCURRENTLY for zero-downtime
        create_count = content.count("CREATE INDEX")
        concurrent_count = content.count("CONCURRENTLY")
        assert concurrent_count >= create_count * 0.8, "Most indexes should use CONCURRENTLY"

    def test_migration_has_if_not_exists(self):
        path = os.path.join(MIGRATIONS_DIR, "001_performance_indexes.sql")
        if not os.path.exists(path):
            pytest.skip("Migration 001 not found")
        with open(path) as f:
            content = f.read()
        create_count = content.count("CREATE INDEX")
        if_not_exists_count = content.count("IF NOT EXISTS")
        assert if_not_exists_count >= create_count * 0.8, "Most indexes should have IF NOT EXISTS"
