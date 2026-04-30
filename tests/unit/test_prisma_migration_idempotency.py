from pathlib import Path


MIGRATIONS_ROOT = Path("apps/services")


def _migration_files() -> list[Path]:
    return sorted(MIGRATIONS_ROOT.glob("*/prisma/migrations/*/migration.sql"))


def test_prisma_create_type_statements_handle_duplicate_objects() -> None:
    failures: list[str] = []

    for path in _migration_files():
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, start=1):
            if line.lstrip().upper().startswith("CREATE TYPE"):
                block_start = max(0, line_number - 1)
                while block_start > 0 and "DO $$" not in lines[block_start]:
                    block_start -= 1
                block_end = line_number - 1
                while block_end < len(lines) - 1 and "END $$;" not in lines[block_end]:
                    block_end += 1
                block = "\n".join(lines[block_start:block_end])
                if "EXCEPTION WHEN duplicate_object" not in block:
                    failures.append(f"{path}:{line_number}: {line.strip()}")

    assert not failures, "CREATE TYPE statements must be duplicate-safe:\n" + "\n".join(failures)


def test_prisma_create_table_and_index_statements_use_if_not_exists() -> None:
    failures: list[str] = []

    for path in _migration_files():
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.lstrip()
            upper = stripped.upper()
            if stripped.startswith("--"):
                continue
            if (upper.startswith("CREATE TABLE") or upper.startswith("CREATE INDEX") or upper.startswith("CREATE UNIQUE INDEX")) and "IF NOT EXISTS" not in upper:
                failures.append(f"{path}:{line_number}: {stripped}")

    assert not failures, "CREATE TABLE/INDEX statements must use IF NOT EXISTS:\n" + "\n".join(failures)


def test_prisma_add_column_statements_use_if_not_exists() -> None:
    failures: list[str] = []

    for path in _migration_files():
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.lstrip()
            upper = stripped.upper()
            if stripped.startswith("--"):
                continue
            if "ADD COLUMN" in upper and "ADD COLUMN IF NOT EXISTS" not in upper:
                failures.append(f"{path}:{line_number}: {stripped}")

    assert not failures, "ALTER TABLE ADD COLUMN statements must use IF NOT EXISTS:\n" + "\n".join(failures)
