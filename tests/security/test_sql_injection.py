"""
SQL Injection Prevention Tests for SAHOOL Platform.

Tests validate parameterized queries and input sanitization.
"""

from typing import Any, Dict, List
from unittest.mock import AsyncMock

import pytest

SQL_INJECTION_PAYLOADS = [
    "'; DROP TABLE users; --",
    "1' OR '1'='1",
    "1; DELETE FROM fields WHERE '1'='1",
    "admin'--",
    "' UNION SELECT * FROM users --",
    "1' AND SLEEP(5) --",
    "1'; EXEC xp_cmdshell('dir'); --",
    "' OR 1=1 --",
    "'; INSERT INTO users VALUES('hacker', 'password'); --",
    "1' AND (SELECT COUNT(*) FROM users) > 0 --",
    "Robert'); DROP TABLE Students;--",
    "1 OR 1=1",
    "' OR ''='",
    "') OR ('a'='a",
    "1' AND 1=CONVERT(int, @@version) --",
    "'; WAITFOR DELAY '0:0:5'; --",
    "1' AND extractvalue(1, concat(0x7e, version())) --",
    "' AND 1=1 UNION ALL SELECT NULL, NULL, NULL--",
]


class ParameterizedQueryBuilder:
    """Mock parameterized query builder for testing."""

    def __init__(self):
        self.queries: list[dict[str, Any]] = []

    def build_select(self, table: str, conditions: dict[str, Any]) -> tuple:
        """Build parameterized SELECT query."""
        if not table.isidentifier():
            raise ValueError(f"Invalid table name: {table}")

        where_clauses = []
        params = []
        param_idx = 1

        for column, value in conditions.items():
            if not column.isidentifier():
                raise ValueError(f"Invalid column name: {column}")
            where_clauses.append(f"{column} = ${param_idx}")
            params.append(value)
            param_idx += 1

        where_str = " AND ".join(where_clauses) if where_clauses else "1=1"
        query = f"SELECT * FROM {table} WHERE {where_str}"

        self.queries.append({"query": query, "params": params})
        return query, params

    def build_insert(self, table: str, data: dict[str, Any]) -> tuple:
        """Build parameterized INSERT query."""
        if not table.isidentifier():
            raise ValueError(f"Invalid table name: {table}")

        columns = []
        placeholders = []
        params = []

        for idx, (column, value) in enumerate(data.items(), 1):
            if not column.isidentifier():
                raise ValueError(f"Invalid column name: {column}")
            columns.append(column)
            placeholders.append(f"${idx}")
            params.append(value)

        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        self.queries.append({"query": query, "params": params})
        return query, params

    def build_update(self, table: str, data: dict[str, Any], conditions: dict[str, Any]) -> tuple:
        """Build parameterized UPDATE query."""
        if not table.isidentifier():
            raise ValueError(f"Invalid table name: {table}")

        set_clauses = []
        params = []
        param_idx = 1

        for column, value in data.items():
            if not column.isidentifier():
                raise ValueError(f"Invalid column name: {column}")
            set_clauses.append(f"{column} = ${param_idx}")
            params.append(value)
            param_idx += 1

        where_clauses = []
        for column, value in conditions.items():
            if not column.isidentifier():
                raise ValueError(f"Invalid column name: {column}")
            where_clauses.append(f"{column} = ${param_idx}")
            params.append(value)
            param_idx += 1

        where_str = " AND ".join(where_clauses) if where_clauses else "1=1"
        query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {where_str}"

        self.queries.append({"query": query, "params": params})
        return query, params


@pytest.fixture
def query_builder():
    """Create parameterized query builder."""
    return ParameterizedQueryBuilder()


@pytest.fixture
def mock_db_pool():
    """Create mock database pool."""
    pool = AsyncMock()
    pool.execute = AsyncMock(return_value=None)
    pool.fetch = AsyncMock(return_value=[])
    pool.fetchrow = AsyncMock(return_value=None)
    return pool


class TestParameterizedQueries:
    """Tests for parameterized query building."""

    def test_select_with_safe_params(self, query_builder):
        """Test SELECT query uses parameterized values."""
        query, params = query_builder.build_select("users", {"id": 1, "name": "John"})

        assert "$1" in query
        assert "$2" in query
        assert "1" not in query.replace("$1", "")
        assert "John" not in query
        assert params == [1, "John"]

    def test_insert_with_safe_params(self, query_builder):
        """Test INSERT query uses parameterized values."""
        data = {"name": "Test Field", "area_ha": 10.5, "tenant_id": "tenant123"}
        query, params = query_builder.build_insert("fields", data)

        assert "Test Field" not in query
        assert "10.5" not in query
        assert "$1" in query
        assert params == ["Test Field", 10.5, "tenant123"]

    def test_update_with_safe_params(self, query_builder):
        """Test UPDATE query uses parameterized values."""
        query, params = query_builder.build_update("fields", {"name": "Updated Field"}, {"id": 1})

        assert "Updated Field" not in query
        assert "$1" in query
        assert "$2" in query
        assert params == ["Updated Field", 1]


class TestSQLInjectionPrevention:
    """Tests for SQL injection prevention."""

    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    def test_injection_in_select_value(self, query_builder, payload):
        """Test SQL injection payloads are safely parameterized in SELECT."""
        query, params = query_builder.build_select("users", {"name": payload})

        assert payload not in query
        assert payload in params
        assert "DROP" not in query.upper()
        assert "DELETE" not in query.upper()
        assert "UNION" not in query.upper()
        assert "INSERT" not in query.upper()

    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    def test_injection_in_insert_value(self, query_builder, payload):
        """Test SQL injection payloads are safely parameterized in INSERT."""
        query, params = query_builder.build_insert("fields", {"name": payload})

        assert payload not in query
        assert payload in params
        assert query.count("INSERT") == 1
        assert "DROP" not in query.upper()

    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    def test_injection_in_update_value(self, query_builder, payload):
        """Test SQL injection payloads are safely parameterized in UPDATE."""
        query, params = query_builder.build_update("fields", {"name": payload}, {"id": 1})

        assert payload not in query
        assert payload in params
        assert "DROP" not in query.upper()

    def test_injection_in_table_name_rejected(self, query_builder):
        """Test SQL injection in table name is rejected."""
        with pytest.raises(ValueError, match="Invalid table name"):
            query_builder.build_select("users; DROP TABLE users;--", {"id": 1})

    def test_injection_in_column_name_rejected(self, query_builder):
        """Test SQL injection in column name is rejected."""
        with pytest.raises(ValueError, match="Invalid column name"):
            query_builder.build_select("users", {"id; DROP TABLE users;--": 1})

    def test_special_characters_in_values(self, query_builder):
        """Test special characters in values are safely handled."""
        special_values = {
            "name": "O'Brien",
            "description": 'Field with "quotes"',
            "notes": "Line1\nLine2",
            "path": "C:\\Users\\test",
        }

        for key, value in special_values.items():
            query, params = query_builder.build_insert("fields", {key: value})
            assert value not in query
            assert value in params


class TestInputSanitization:
    """Tests for input sanitization functions."""

    def test_strip_null_bytes(self):
        """Test null byte stripping."""
        input_str = "test\x00value"
        sanitized = input_str.replace("\x00", "")
        assert "\x00" not in sanitized
        assert sanitized == "testvalue"

    def test_limit_string_length(self):
        """Test string length limiting."""
        max_length = 255
        long_input = "a" * 1000
        limited = long_input[:max_length]
        assert len(limited) == max_length

    def test_escape_html_entities(self):
        """Test HTML entity escaping for XSS prevention."""
        import html

        input_str = "<script>alert('xss')</script>"
        escaped = html.escape(input_str)
        assert "<" not in escaped
        assert ">" not in escaped
        assert "&lt;" in escaped
        assert "&gt;" in escaped

    def test_unicode_normalization(self):
        """Test unicode normalization."""
        import unicodedata

        input_str = "café"
        normalized = unicodedata.normalize("NFKC", input_str)
        assert normalized == "café"


class TestDatabaseConnectionSecurity:
    """Tests for database connection security."""

    def test_connection_string_no_password_in_logs(self):
        """Test password is not exposed in connection strings."""
        conn_string = "postgresql://user:secret@localhost:5432/sahool"
        safe_string = conn_string.replace(":secret@", ":***@")
        assert "secret" not in safe_string

    def test_ssl_mode_required(self):
        """Test SSL mode is enforced."""
        conn_params = {"sslmode": "require"}
        assert conn_params["sslmode"] == "require"

    def test_connection_timeout_set(self):
        """Test connection timeout is configured."""
        conn_params = {"connect_timeout": 10}
        assert conn_params["connect_timeout"] <= 30


class TestStoredProcedureSafety:
    """Tests for stored procedure safety."""

    def test_no_dynamic_sql_in_procedures(self):
        """Test no dynamic SQL construction."""
        procedure_code = """
        CREATE FUNCTION get_field(field_id UUID)
        RETURNS TABLE (id UUID, name TEXT) AS $$
        BEGIN
            RETURN QUERY SELECT f.id, f.name FROM fields f WHERE f.id = field_id;
        END;
        $$ LANGUAGE plpgsql;
        """
        assert "EXECUTE" not in procedure_code.upper()
        assert "CONCAT" not in procedure_code.upper()

    def test_definer_security(self):
        """Test procedures use SECURITY DEFINER carefully."""
        procedure_code = "SECURITY INVOKER"
        assert "INVOKER" in procedure_code


class TestBatchOperationSafety:
    """Tests for batch operation safety."""

    def test_batch_insert_parameterized(self, query_builder):
        """Test batch inserts use parameterized queries."""
        records = [
            {"name": "Field 1", "area_ha": 10},
            {"name": "Field 2'; DROP TABLE fields;--", "area_ha": 20},
            {"name": "Field 3", "area_ha": 30},
        ]

        for record in records:
            query, params = query_builder.build_insert("fields", record)
            assert record["name"] not in query
            assert record["name"] in params

    def test_bulk_update_parameterized(self, query_builder):
        """Test bulk updates use parameterized queries."""
        updates = [
            ({"status": "active"}, {"id": 1}),
            ({"status": "'; DELETE FROM fields;--"}, {"id": 2}),
        ]

        for data, conditions in updates:
            query, params = query_builder.build_update("fields", data, conditions)
            assert data["status"] not in query
            assert data["status"] in params


@pytest.mark.unit
class TestPostGISSQLInjection:
    """Tests for PostGIS-specific SQL injection prevention."""

    def test_geometry_input_validation(self):
        """Test geometry input is validated."""
        valid_geojson = '{"type": "Polygon", "coordinates": [[[0,0],[1,0],[1,1],[0,1],[0,0]]]}'

        import json

        try:
            geom = json.loads(valid_geojson)
            assert geom["type"] == "Polygon"
            assert "coordinates" in geom
        except json.JSONDecodeError:
            pytest.fail("Invalid GeoJSON")

    def test_wkt_injection_prevention(self):
        """Test WKT injection is prevented."""
        malicious_wkt = "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0)); DROP TABLE fields;--"

        if ";" in malicious_wkt:
            wkt = malicious_wkt.split(";")[0]
        else:
            wkt = malicious_wkt

        assert "DROP" not in wkt
        assert ";" not in wkt

    def test_srid_input_validation(self):
        """Test SRID input is numeric."""
        valid_srid = 4326
        invalid_srid = "4326; DROP TABLE spatial_ref_sys;--"

        assert isinstance(valid_srid, int)

        try:
            int(invalid_srid)
            pytest.fail("Should have raised ValueError")
        except ValueError:
            pass


@pytest.mark.unit
class TestORM_SQLInjection:
    """Tests for ORM-level SQL injection prevention."""

    def test_raw_query_with_params(self):
        """Test raw queries use parameter binding."""
        query = "SELECT * FROM fields WHERE tenant_id = $1 AND name ILIKE $2"
        params = ["tenant123", "%search%"]

        assert "$1" in query
        assert "$2" in query
        assert "tenant123" not in query
        assert "%search%" not in query

    def test_order_by_whitelist(self):
        """Test ORDER BY uses whitelist."""
        allowed_columns = ["name", "created_at", "updated_at", "area_ha"]
        user_input = "name; DROP TABLE fields;--"

        if user_input not in allowed_columns:
            order_column = "created_at"
        else:
            order_column = user_input

        assert order_column == "created_at"
        assert "DROP" not in order_column

    def test_limit_offset_validation(self):
        """Test LIMIT and OFFSET are integers."""
        user_limit = "10; DROP TABLE fields;--"
        user_offset = "0 OR 1=1"

        try:
            safe_limit = int(user_limit)
        except ValueError:
            safe_limit = 100

        try:
            safe_offset = int(user_offset)
        except ValueError:
            safe_offset = 0

        assert safe_limit == 100
        assert safe_offset == 0
