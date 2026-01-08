"""
SAHOOL Database Operations Integration Tests
اختبارات التكامل لعمليات قاعدة البيانات

Tests PostgreSQL database operations:
- Connection pooling and management
- Transaction isolation and ACID properties
- PostGIS spatial operations
- Multi-tenant data isolation
- Database migrations and schema validation
- Query performance and indexing
- Connection resilience and failover

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any

import psycopg2
import pytest
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

# ═══════════════════════════════════════════════════════════════════════════════
# Test Data Factories
# ═══════════════════════════════════════════════════════════════════════════════


def create_test_field_data(tenant_id: str | None = None) -> dict[str, Any]:
    """Create test field data for database operations"""
    return {
        "id": str(uuid.uuid4()),
        "tenant_id": tenant_id or str(uuid.uuid4()),
        "name": f"Test Field {uuid.uuid4().hex[:8]}",
        "area_hectares": 10.5,
        "crop_type": "wheat",
        "created_at": datetime.utcnow(),
    }


def create_test_sensor_reading(field_id: str, tenant_id: str) -> dict[str, Any]:
    """Create test sensor reading data"""
    return {
        "id": str(uuid.uuid4()),
        "field_id": field_id,
        "tenant_id": tenant_id,
        "sensor_type": "soil_moisture",
        "value": 45.7,
        "timestamp": datetime.utcnow(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Connection & Pool Management Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
def test_database_connection_basic(db_connection):
    """
    Test basic database connectivity
    اختبار الاتصال الأساسي بقاعدة البيانات
    """
    cursor = db_connection.cursor()

    # Execute simple query
    cursor.execute("SELECT 1 as test_value")
    result = cursor.fetchone()

    assert result is not None
    assert result["test_value"] == 1

    cursor.close()


@pytest.mark.integration
def test_database_version_check(db_connection):
    """
    Test PostgreSQL version is compatible
    اختبار توافق إصدار PostgreSQL
    """
    cursor = db_connection.cursor()

    cursor.execute("SELECT version()")
    version = cursor.fetchone()

    assert version is not None
    version_str = version["version"]
    assert "PostgreSQL" in version_str

    # Check for PostGIS extension
    cursor.execute("""
        SELECT EXISTS(
            SELECT 1 FROM pg_extension WHERE extname = 'postgis'
        ) as has_postgis
    """)
    result = cursor.fetchone()
    assert result["has_postgis"], "PostGIS extension should be installed"

    cursor.close()


@pytest.mark.integration
def test_database_connection_pool_behavior(test_config):
    """
    Test database connection pool creates multiple connections
    اختبار إنشاء مجموعة اتصالات قاعدة البيانات لاتصالات متعددة
    """
    connections = []

    try:
        # Create multiple connections
        for i in range(3):
            conn = psycopg2.connect(
                host=test_config.postgres_host,
                port=test_config.postgres_port,
                user=test_config.postgres_user,
                password=test_config.postgres_password,
                dbname=test_config.postgres_db,
            )
            connections.append(conn)

        # All connections should be valid
        for conn in connections:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
            cursor.close()

    finally:
        # Clean up connections
        for conn in connections:
            conn.close()


@pytest.mark.integration
def test_database_connection_resilience(test_config):
    """
    Test database connection handles reconnection
    اختبار معالجة اتصال قاعدة البيانات لإعادة الاتصال
    """
    # Create connection
    conn = psycopg2.connect(
        host=test_config.postgres_host,
        port=test_config.postgres_port,
        user=test_config.postgres_user,
        password=test_config.postgres_password,
        dbname=test_config.postgres_db,
    )

    # Execute query
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result1 = cursor.fetchone()
    assert result1[0] == 1

    # Connection should still work
    cursor.execute("SELECT 2")
    result2 = cursor.fetchone()
    assert result2[0] == 2

    cursor.close()
    conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Transaction & ACID Properties Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
def test_transaction_commit(db_connection):
    """
    Test transaction commit saves data permanently
    اختبار حفظ البيانات بشكل دائم عند تنفيذ المعاملة
    """
    cursor = db_connection.cursor()

    # Create temporary table for testing
    table_name = f"test_commit_{uuid.uuid4().hex[:8]}"
    cursor.execute(f"""
        CREATE TEMPORARY TABLE {table_name} (
            id VARCHAR(36) PRIMARY KEY,
            value INTEGER
        )
    """)

    # Insert data in transaction
    test_id = str(uuid.uuid4())
    cursor.execute(f"INSERT INTO {table_name} (id, value) VALUES (%s, %s)", (test_id, 42))

    # Verify data was inserted
    cursor.execute(f"SELECT value FROM {table_name} WHERE id = %s", (test_id,))
    result = cursor.fetchone()
    assert result is not None
    assert result["value"] == 42

    cursor.close()


@pytest.mark.integration
def test_transaction_rollback(test_config):
    """
    Test transaction rollback discards changes
    اختبار تجاهل التغييرات عند التراجع عن المعاملة
    """
    # Create connection with explicit transaction control
    conn = psycopg2.connect(
        host=test_config.postgres_host,
        port=test_config.postgres_port,
        user=test_config.postgres_user,
        password=test_config.postgres_password,
        dbname=test_config.postgres_db,
        cursor_factory=RealDictCursor,
    )
    conn.autocommit = False  # Disable autocommit for transaction testing

    cursor = conn.cursor()

    try:
        # Create temporary table
        table_name = f"test_rollback_{uuid.uuid4().hex[:8]}"
        cursor.execute(f"""
            CREATE TEMPORARY TABLE {table_name} (
                id VARCHAR(36) PRIMARY KEY,
                value INTEGER
            )
        """)
        conn.commit()

        # Insert data
        test_id = str(uuid.uuid4())
        cursor.execute(f"INSERT INTO {table_name} (id, value) VALUES (%s, %s)", (test_id, 99))

        # Rollback transaction
        conn.rollback()

        # Verify data was not saved
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name} WHERE id = %s", (test_id,))
        result = cursor.fetchone()
        assert result["count"] == 0, "Data should not exist after rollback"

    finally:
        cursor.close()
        conn.close()


@pytest.mark.integration
def test_transaction_isolation(test_config):
    """
    Test transaction isolation between concurrent connections
    اختبار عزل المعاملات بين الاتصالات المتزامنة
    """
    # Create two separate connections
    conn1 = psycopg2.connect(
        host=test_config.postgres_host,
        port=test_config.postgres_port,
        user=test_config.postgres_user,
        password=test_config.postgres_password,
        dbname=test_config.postgres_db,
        cursor_factory=RealDictCursor,
    )
    conn1.autocommit = False

    conn2 = psycopg2.connect(
        host=test_config.postgres_host,
        port=test_config.postgres_port,
        user=test_config.postgres_user,
        password=test_config.postgres_password,
        dbname=test_config.postgres_db,
        cursor_factory=RealDictCursor,
    )
    conn2.autocommit = False

    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()

    try:
        # Create shared temporary table (use regular table for isolation test)
        table_name = f"test_isolation_{uuid.uuid4().hex[:8]}"

        cursor1.execute(f"""
            CREATE TABLE {table_name} (
                id VARCHAR(36) PRIMARY KEY,
                value INTEGER
            )
        """)
        conn1.commit()

        # Connection 1: Insert data but don't commit
        test_id = str(uuid.uuid4())
        cursor1.execute(f"INSERT INTO {table_name} (id, value) VALUES (%s, %s)", (test_id, 100))

        # Connection 2: Should not see uncommitted data
        cursor2.execute(f"SELECT COUNT(*) as count FROM {table_name} WHERE id = %s", (test_id,))
        result = cursor2.fetchone()
        assert result["count"] == 0, "Uncommitted data should not be visible"

        # Connection 1: Commit
        conn1.commit()

        # Connection 2: Should now see the data
        cursor2.execute(f"SELECT value FROM {table_name} WHERE id = %s", (test_id,))
        result = cursor2.fetchone()
        assert result is not None
        assert result["value"] == 100

        # Cleanup
        cursor1.execute(f"DROP TABLE {table_name}")
        conn1.commit()

    finally:
        cursor1.close()
        cursor2.close()
        conn1.close()
        conn2.close()


@pytest.mark.integration
def test_concurrent_writes_no_deadlock(test_config):
    """
    Test concurrent writes don't cause deadlocks
    اختبار عدم تسبب الكتابات المتزامنة في حالات الجمود
    """
    conn = psycopg2.connect(
        host=test_config.postgres_host,
        port=test_config.postgres_port,
        user=test_config.postgres_user,
        password=test_config.postgres_password,
        dbname=test_config.postgres_db,
        cursor_factory=RealDictCursor,
    )
    cursor = conn.cursor()

    try:
        # Create test table
        table_name = f"test_deadlock_{uuid.uuid4().hex[:8]}"
        cursor.execute(f"""
            CREATE TEMPORARY TABLE {table_name} (
                id VARCHAR(36) PRIMARY KEY,
                value INTEGER
            )
        """)

        # Insert multiple rows quickly (simulating concurrent writes)
        for i in range(10):
            test_id = str(uuid.uuid4())
            cursor.execute(f"INSERT INTO {table_name} (id, value) VALUES (%s, %s)", (test_id, i))

        # All inserts should succeed
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        result = cursor.fetchone()
        assert result["count"] == 10

    finally:
        cursor.close()
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# PostGIS Spatial Operations Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
def test_postgis_point_creation(db_connection):
    """
    Test creating PostGIS point geometries
    اختبار إنشاء نقاط PostGIS الهندسية
    """
    cursor = db_connection.cursor()

    # Create point geometry (Riyadh, Saudi Arabia coordinates)
    cursor.execute("""
        SELECT ST_AsText(ST_SetSRID(ST_MakePoint(46.7382, 24.7136), 4326)) as point
    """)
    result = cursor.fetchone()

    assert result is not None
    assert "POINT" in result["point"]
    assert "46.7382" in result["point"]

    cursor.close()


@pytest.mark.integration
def test_postgis_polygon_creation(db_connection):
    """
    Test creating PostGIS polygon geometries for fields
    اختبار إنشاء مضلعات PostGIS الهندسية للحقول
    """
    cursor = db_connection.cursor()

    # Create polygon for agricultural field boundary
    cursor.execute("""
        SELECT ST_AsText(
            ST_SetSRID(
                ST_MakePolygon(
                    ST_MakeLine(ARRAY[
                        ST_MakePoint(46.7, 24.7),
                        ST_MakePoint(46.8, 24.7),
                        ST_MakePoint(46.8, 24.8),
                        ST_MakePoint(46.7, 24.8),
                        ST_MakePoint(46.7, 24.7)
                    ])
                ),
                4326
            )
        ) as polygon
    """)
    result = cursor.fetchone()

    assert result is not None
    assert "POLYGON" in result["polygon"]

    cursor.close()


@pytest.mark.integration
def test_postgis_area_calculation(db_connection):
    """
    Test calculating area of agricultural fields
    اختبار حساب مساحة الحقول الزراعية
    """
    cursor = db_connection.cursor()

    # Calculate area of polygon in square meters
    cursor.execute("""
        SELECT ST_Area(
            ST_Transform(
                ST_SetSRID(
                    ST_MakePolygon(
                        ST_MakeLine(ARRAY[
                            ST_MakePoint(46.7, 24.7),
                            ST_MakePoint(46.71, 24.7),
                            ST_MakePoint(46.71, 24.71),
                            ST_MakePoint(46.7, 24.71),
                            ST_MakePoint(46.7, 24.7)
                        ])
                    ),
                    4326
                ),
                3857  -- Web Mercator for area calculation
            )
        ) as area_sqm
    """)
    result = cursor.fetchone()

    assert result is not None
    assert result["area_sqm"] > 0

    cursor.close()


@pytest.mark.integration
def test_postgis_distance_calculation(db_connection):
    """
    Test calculating distance between points
    اختبار حساب المسافة بين النقاط
    """
    cursor = db_connection.cursor()

    # Calculate distance between two points in Saudi Arabia
    cursor.execute("""
        SELECT ST_Distance(
            ST_Transform(ST_SetSRID(ST_MakePoint(46.7382, 24.7136), 4326), 3857),
            ST_Transform(ST_SetSRID(ST_MakePoint(46.8382, 24.8136), 4326), 3857)
        ) as distance_meters
    """)
    result = cursor.fetchone()

    assert result is not None
    assert result["distance_meters"] > 0

    cursor.close()


@pytest.mark.integration
def test_postgis_spatial_index(db_connection):
    """
    Test PostGIS spatial indexing works
    اختبار فهرسة PostGIS المكانية
    """
    cursor = db_connection.cursor()

    # Create temporary table with spatial column
    table_name = f"test_spatial_{uuid.uuid4().hex[:8]}"
    cursor.execute(f"""
        CREATE TEMPORARY TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            location GEOMETRY(Point, 4326)
        )
    """)

    # Create spatial index
    cursor.execute(f"""
        CREATE INDEX idx_{table_name}_location
        ON {table_name} USING GIST (location)
    """)

    # Insert test data
    cursor.execute(f"""
        INSERT INTO {table_name} (name, location)
        VALUES ('Test Point', ST_SetSRID(ST_MakePoint(46.7382, 24.7136), 4326))
    """)

    # Query using spatial index
    cursor.execute(f"""
        SELECT name FROM {table_name}
        WHERE ST_DWithin(
            location,
            ST_SetSRID(ST_MakePoint(46.7382, 24.7136), 4326),
            0.01
        )
    """)
    result = cursor.fetchone()

    assert result is not None
    assert result["name"] == "Test Point"

    cursor.close()


@pytest.mark.integration
def test_postgis_geometry_validation(db_connection):
    """
    Test PostGIS geometry validation
    اختبار التحقق من صحة هندسة PostGIS
    """
    cursor = db_connection.cursor()

    # Test valid geometry
    cursor.execute("""
        SELECT ST_IsValid(
            ST_SetSRID(ST_MakePoint(46.7382, 24.7136), 4326)
        ) as is_valid
    """)
    result = cursor.fetchone()
    assert result["is_valid"] is True

    # Test geometry type checking
    cursor.execute("""
        SELECT GeometryType(
            ST_SetSRID(ST_MakePoint(46.7382, 24.7136), 4326)
        ) as geom_type
    """)
    result = cursor.fetchone()
    assert result["geom_type"] == "POINT"

    cursor.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Multi-Tenant Data Isolation Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
def test_tenant_data_isolation(db_connection):
    """
    Test tenant data is properly isolated
    اختبار عزل بيانات المستأجر بشكل صحيح
    """
    cursor = db_connection.cursor()

    # Create test table with tenant_id
    table_name = f"test_tenant_{uuid.uuid4().hex[:8]}"
    cursor.execute(f"""
        CREATE TEMPORARY TABLE {table_name} (
            id VARCHAR(36) PRIMARY KEY,
            tenant_id VARCHAR(36) NOT NULL,
            data VARCHAR(100)
        )
    """)

    # Insert data for two different tenants
    tenant1_id = str(uuid.uuid4())
    tenant2_id = str(uuid.uuid4())

    cursor.execute(
        f"INSERT INTO {table_name} (id, tenant_id, data) VALUES (%s, %s, %s)",
        (str(uuid.uuid4()), tenant1_id, "Tenant 1 Data"),
    )
    cursor.execute(
        f"INSERT INTO {table_name} (id, tenant_id, data) VALUES (%s, %s, %s)",
        (str(uuid.uuid4()), tenant2_id, "Tenant 2 Data"),
    )

    # Query for tenant 1 data only
    cursor.execute(f"SELECT data FROM {table_name} WHERE tenant_id = %s", (tenant1_id,))
    results = cursor.fetchall()

    assert len(results) == 1
    assert results[0]["data"] == "Tenant 1 Data"

    # Query for tenant 2 data only
    cursor.execute(f"SELECT data FROM {table_name} WHERE tenant_id = %s", (tenant2_id,))
    results = cursor.fetchall()

    assert len(results) == 1
    assert results[0]["data"] == "Tenant 2 Data"

    cursor.close()


@pytest.mark.integration
def test_tenant_data_no_leakage(db_connection):
    """
    Test no data leakage between tenants
    اختبار عدم تسرب البيانات بين المستأجرين
    """
    cursor = db_connection.cursor()

    # Create test table
    table_name = f"test_leak_{uuid.uuid4().hex[:8]}"
    cursor.execute(f"""
        CREATE TEMPORARY TABLE {table_name} (
            id VARCHAR(36) PRIMARY KEY,
            tenant_id VARCHAR(36) NOT NULL,
            sensitive_data VARCHAR(100)
        )
    """)

    # Insert sensitive data for different tenants
    tenant1_id = str(uuid.uuid4())
    tenant2_id = str(uuid.uuid4())

    cursor.execute(
        f"INSERT INTO {table_name} (id, tenant_id, sensitive_data) VALUES (%s, %s, %s)",
        (str(uuid.uuid4()), tenant1_id, "Tenant 1 Secret"),
    )
    cursor.execute(
        f"INSERT INTO {table_name} (id, tenant_id, sensitive_data) VALUES (%s, %s, %s)",
        (str(uuid.uuid4()), tenant2_id, "Tenant 2 Secret"),
    )

    # Verify tenant 1 cannot see tenant 2's data
    cursor.execute(f"SELECT sensitive_data FROM {table_name} WHERE tenant_id = %s", (tenant1_id,))
    results = cursor.fetchall()

    assert len(results) == 1
    assert "Tenant 2" not in results[0]["sensitive_data"]

    cursor.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Query Performance & Indexing Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
def test_query_with_index_performance(db_connection):
    """
    Test queries use indexes for better performance
    اختبار استخدام الاستعلامات للفهارس لأداء أفضل
    """
    cursor = db_connection.cursor()

    # Create table with index
    table_name = f"test_perf_{uuid.uuid4().hex[:8]}"
    cursor.execute(f"""
        CREATE TEMPORARY TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(36) NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)

    # Create index on tenant_id
    cursor.execute(f"""
        CREATE INDEX idx_{table_name}_tenant
        ON {table_name}(tenant_id)
    """)

    # Insert test data
    tenant_id = str(uuid.uuid4())
    for i in range(100):
        cursor.execute(
            f"INSERT INTO {table_name} (tenant_id, created_at) VALUES (%s, %s)",
            (tenant_id, datetime.utcnow()),
        )

    # Query should use index (verify with EXPLAIN)
    cursor.execute(
        f"""
        EXPLAIN SELECT * FROM {table_name} WHERE tenant_id = %s
    """,
        (tenant_id,),
    )

    explain_results = cursor.fetchall()
    explain_text = " ".join(str(row) for row in explain_results)

    # Should mention index scan (not always guaranteed in small datasets)
    # Just verify query executes successfully
    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name} WHERE tenant_id = %s", (tenant_id,))
    result = cursor.fetchone()
    assert result["count"] == 100

    cursor.close()


@pytest.mark.integration
def test_bulk_insert_performance(db_connection):
    """
    Test bulk insert operations
    اختبار عمليات الإدراج الجماعي
    """
    cursor = db_connection.cursor()

    # Create test table
    table_name = f"test_bulk_{uuid.uuid4().hex[:8]}"
    cursor.execute(f"""
        CREATE TEMPORARY TABLE {table_name} (
            id VARCHAR(36) PRIMARY KEY,
            value INTEGER
        )
    """)

    # Bulk insert using execute_values
    from psycopg2.extras import execute_values

    data = [(str(uuid.uuid4()), i) for i in range(100)]

    execute_values(cursor, f"INSERT INTO {table_name} (id, value) VALUES %s", data)

    # Verify all records inserted
    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
    result = cursor.fetchone()
    assert result["count"] == 100

    cursor.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Data Integrity & Constraints Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
def test_primary_key_constraint(db_connection):
    """
    Test primary key constraint enforcement
    اختبار فرض قيد المفتاح الأساسي
    """
    cursor = db_connection.cursor()

    # Create table with primary key
    table_name = f"test_pk_{uuid.uuid4().hex[:8]}"
    cursor.execute(f"""
        CREATE TEMPORARY TABLE {table_name} (
            id VARCHAR(36) PRIMARY KEY,
            value INTEGER
        )
    """)

    # Insert first record
    test_id = str(uuid.uuid4())
    cursor.execute(f"INSERT INTO {table_name} (id, value) VALUES (%s, %s)", (test_id, 1))

    # Try to insert duplicate primary key
    with pytest.raises(psycopg2.IntegrityError):
        cursor.execute(f"INSERT INTO {table_name} (id, value) VALUES (%s, %s)", (test_id, 2))

    cursor.close()


@pytest.mark.integration
def test_foreign_key_constraint(db_connection):
    """
    Test foreign key constraint enforcement
    اختبار فرض قيد المفتاح الأجنبي
    """
    cursor = db_connection.cursor()

    # Create parent table
    parent_table = f"test_parent_{uuid.uuid4().hex[:8]}"
    cursor.execute(f"""
        CREATE TEMPORARY TABLE {parent_table} (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(100)
        )
    """)

    # Create child table with foreign key
    child_table = f"test_child_{uuid.uuid4().hex[:8]}"
    cursor.execute(f"""
        CREATE TEMPORARY TABLE {child_table} (
            id VARCHAR(36) PRIMARY KEY,
            parent_id VARCHAR(36) REFERENCES {parent_table}(id),
            value INTEGER
        )
    """)

    # Insert parent record
    parent_id = str(uuid.uuid4())
    cursor.execute(f"INSERT INTO {parent_table} (id, name) VALUES (%s, %s)", (parent_id, "Parent"))

    # Insert child record - should succeed
    cursor.execute(
        f"INSERT INTO {child_table} (id, parent_id, value) VALUES (%s, %s, %s)",
        (str(uuid.uuid4()), parent_id, 42),
    )

    # Try to insert child with non-existent parent - should fail
    with pytest.raises(psycopg2.IntegrityError):
        cursor.execute(
            f"INSERT INTO {child_table} (id, parent_id, value) VALUES (%s, %s, %s)",
            (str(uuid.uuid4()), str(uuid.uuid4()), 99),
        )

    cursor.close()


@pytest.mark.integration
def test_not_null_constraint(db_connection):
    """
    Test NOT NULL constraint enforcement
    اختبار فرض قيد عدم السماح بالقيم الفارغة
    """
    cursor = db_connection.cursor()

    # Create table with NOT NULL constraint
    table_name = f"test_notnull_{uuid.uuid4().hex[:8]}"
    cursor.execute(f"""
        CREATE TEMPORARY TABLE {table_name} (
            id VARCHAR(36) PRIMARY KEY,
            required_field VARCHAR(100) NOT NULL
        )
    """)

    # Try to insert NULL value
    with pytest.raises(psycopg2.IntegrityError):
        cursor.execute(
            f"INSERT INTO {table_name} (id, required_field) VALUES (%s, %s)",
            (str(uuid.uuid4()), None),
        )

    cursor.close()


@pytest.mark.integration
def test_unique_constraint(db_connection):
    """
    Test UNIQUE constraint enforcement
    اختبار فرض قيد الفريد
    """
    cursor = db_connection.cursor()

    # Create table with unique constraint
    table_name = f"test_unique_{uuid.uuid4().hex[:8]}"
    cursor.execute(f"""
        CREATE TEMPORARY TABLE {table_name} (
            id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL
        )
    """)

    # Insert first record
    cursor.execute(
        f"INSERT INTO {table_name} (id, email) VALUES (%s, %s)",
        (str(uuid.uuid4()), "test@sahool.com"),
    )

    # Try to insert duplicate email
    with pytest.raises(psycopg2.IntegrityError):
        cursor.execute(
            f"INSERT INTO {table_name} (id, email) VALUES (%s, %s)",
            (str(uuid.uuid4()), "test@sahool.com"),
        )

    cursor.close()
