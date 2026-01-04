"""
GlobalGAP Compliance Database Usage Examples
أمثلة على استخدام قاعدة بيانات الامتثال لـ GlobalGAP

This file demonstrates how to use the database repositories.
يوضح هذا الملف كيفية استخدام مستودعات قاعدة البيانات.
"""

import asyncio
from datetime import date, datetime, timedelta
from uuid import uuid4

# Import database components
from src.database import (
    checklist_repo,
    close_pool,
    compliance_repo,
    db_health_check,
    init_db,
    non_conformance_repo,
    registrations_repo,
    transaction,
)


async def example_1_create_registration():
    """
    Example 1: Create a new GlobalGAP registration
    مثال 1: إنشاء تسجيل GlobalGAP جديد
    """
    print("\n=== Example 1: Create Registration ===")

    farm_id = uuid4()
    registration = await registrations_repo.create(
        farm_id=farm_id,
        ggn="4052852123456",
        registration_date=datetime.now(),
        certificate_status="ACTIVE",
        valid_from=date.today(),
        valid_to=date.today() + timedelta(days=365),
        scope="FRUIT_VEGETABLES",
    )

    print(f"Created registration: {registration['id']}")
    print(f"GGN: {registration['ggn']}")
    print(f"Status: {registration['certificate_status']}")

    return registration


async def example_2_create_compliance_audit(registration_id):
    """
    Example 2: Create a compliance audit record
    مثال 2: إنشاء سجل تدقيق امتثال
    """
    print("\n=== Example 2: Create Compliance Audit ===")

    compliance = await compliance_repo.create(
        registration_id=registration_id,
        checklist_version="6.0",
        audit_date=date.today(),
        major_must_score=98.5,
        minor_must_score=95.0,
        overall_compliance=96.5,
        auditor_notes="Excellent compliance. Minor improvements needed in documentation.",
    )

    print(f"Created compliance record: {compliance['id']}")
    print(f"Overall compliance: {compliance['overall_compliance']}%")
    print(f"Audit date: {compliance['audit_date']}")

    return compliance


async def example_3_add_checklist_responses(compliance_record_id):
    """
    Example 3: Add checklist item responses
    مثال 3: إضافة استجابات عناصر قائمة التحقق
    """
    print("\n=== Example 3: Add Checklist Responses ===")

    # Single response
    response1 = await checklist_repo.create(
        compliance_record_id=compliance_record_id,
        checklist_item_id="FV.1.1.1",
        response="COMPLIANT",
        evidence_path="/documents/evidence/FV_1_1_1.pdf",
        notes="All legal compliance certificates verified",
    )

    # Batch responses
    responses_data = [
        {
            "checklist_item_id": "FV.2.1.1",
            "response": "COMPLIANT",
            "evidence_path": "/documents/evidence/FV_2_1_1.pdf",
            "notes": "Risk assessment completed",
        },
        {
            "checklist_item_id": "FV.3.1.1",
            "response": "NON_COMPLIANT",
            "notes": "Traceability system needs improvement",
        },
        {
            "checklist_item_id": "FV.4.1.1",
            "response": "NOT_APPLICABLE",
            "notes": "No seeds/propagation material used",
        },
    ]

    batch_responses = await checklist_repo.create_batch(
        compliance_record_id=compliance_record_id, responses=responses_data
    )

    print(f"Created {len(batch_responses) + 1} checklist responses")
    print(
        f"Non-compliant items: {sum(1 for r in batch_responses if r['response'] == 'NON_COMPLIANT')}"
    )

    return batch_responses


async def example_4_create_non_conformance(compliance_record_id):
    """
    Example 4: Create a non-conformance
    مثال 4: إنشاء عدم مطابقة
    """
    print("\n=== Example 4: Create Non-Conformance ===")

    nc = await non_conformance_repo.create(
        compliance_record_id=compliance_record_id,
        checklist_item_id="FV.3.1.1",
        severity="MINOR",
        description="Traceability records incomplete for some products",
        corrective_action="Implement digital traceability system",
        due_date=date.today() + timedelta(days=30),
        status="IN_PROGRESS",
    )

    print(f"Created non-conformance: {nc['id']}")
    print(f"Severity: {nc['severity']}")
    print(f"Due date: {nc['due_date']}")
    print(f"Status: {nc['status']}")

    return nc


async def example_5_query_operations():
    """
    Example 5: Various query operations
    مثال 5: عمليات الاستعلام المختلفة
    """
    print("\n=== Example 5: Query Operations ===")

    # Get active registrations
    active_registrations = await registrations_repo.get_active_registrations()
    print(f"Active registrations: {len(active_registrations)}")

    # Get expiring certificates
    expiring = await registrations_repo.get_expiring_soon(days=60)
    print(f"Certificates expiring in 60 days: {len(expiring)}")

    # Get low compliance records
    low_compliance = await compliance_repo.get_low_compliance_records(threshold=85.0)
    print(f"Records with compliance < 85%: {len(low_compliance)}")

    # Get open non-conformances
    open_ncs = await non_conformance_repo.get_open_non_conformances()
    print(f"Open non-conformances: {len(open_ncs)}")

    # Get overdue non-conformances
    overdue_ncs = await non_conformance_repo.get_overdue_non_conformances()
    print(f"Overdue non-conformances: {len(overdue_ncs)}")


async def example_6_update_operations(registration_id, nc_id):
    """
    Example 6: Update operations
    مثال 6: عمليات التحديث
    """
    print("\n=== Example 6: Update Operations ===")

    # Update registration status
    updated_reg = await registrations_repo.update_status(
        registration_id=registration_id,
        status="ACTIVE",
        valid_to=date.today() + timedelta(days=730),
    )
    print(f"Updated registration status: {updated_reg['certificate_status']}")

    # Resolve non-conformance
    resolved_nc = await non_conformance_repo.resolve(
        nc_id=nc_id,
        corrective_action="Digital traceability system implemented and tested successfully",
        resolved_date=date.today(),
    )
    print(f"Resolved non-conformance: {resolved_nc['status']}")


async def example_7_transaction_usage(compliance_record_id):
    """
    Example 7: Using transactions for atomic operations
    مثال 7: استخدام المعاملات للعمليات الذرية
    """
    print("\n=== Example 7: Transaction Usage ===")

    # Create multiple non-conformances in a single transaction
    async with transaction() as conn:
        nc1 = await conn.fetchrow(
            """
            INSERT INTO non_conformances (
                compliance_record_id, checklist_item_id, severity,
                description, status
            )
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            compliance_record_id,
            "FV.5.1.1",
            "MAJOR",
            "Worker health and safety training not documented",
            "OPEN",
        )

        nc2 = await conn.fetchrow(
            """
            INSERT INTO non_conformances (
                compliance_record_id, checklist_item_id, severity,
                description, status
            )
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            compliance_record_id,
            "FV.6.1.1",
            "MINOR",
            "Some irrigation records missing",
            "OPEN",
        )

        print(f"Created {2} non-conformances in transaction")


async def example_8_health_check():
    """
    Example 8: Database health check
    مثال 8: فحص صحة قاعدة البيانات
    """
    print("\n=== Example 8: Health Check ===")

    health = await db_health_check()
    print(f"Database status: {health['status']}")
    print(f"Pool size: {health.get('pool_size', 'N/A')}")
    print(f"Pool free: {health.get('pool_free', 'N/A')}")
    print(f"Pool idle: {health.get('pool_idle', 'N/A')}")


async def example_9_analytics_queries():
    """
    Example 9: Complex analytics queries
    مثال 9: استعلامات التحليلات المعقدة
    """
    print("\n=== Example 9: Analytics Queries ===")

    from src.database import get_connection

    async with get_connection() as conn:
        # Average compliance score by scope
        results = await conn.fetch(
            """
            SELECT
                gr.scope,
                COUNT(DISTINCT cr.id) as audit_count,
                AVG(cr.overall_compliance) as avg_compliance,
                MIN(cr.overall_compliance) as min_compliance,
                MAX(cr.overall_compliance) as max_compliance
            FROM globalgap_registrations gr
            JOIN compliance_records cr ON gr.id = cr.registration_id
            WHERE cr.overall_compliance IS NOT NULL
            GROUP BY gr.scope
            ORDER BY avg_compliance DESC
        """
        )

        print("\nCompliance by Scope:")
        for row in results:
            print(
                f"  {row['scope']}: {row['avg_compliance']:.2f}% avg "
                f"({row['audit_count']} audits)"
            )

        # Most common non-conformances
        nc_results = await conn.fetch(
            """
            SELECT
                checklist_item_id,
                severity,
                COUNT(*) as occurrence_count
            FROM non_conformances
            WHERE status IN ('OPEN', 'IN_PROGRESS')
            GROUP BY checklist_item_id, severity
            ORDER BY occurrence_count DESC
            LIMIT 5
        """
        )

        print("\nTop Non-Conformances:")
        for row in nc_results:
            print(
                f"  {row['checklist_item_id']} ({row['severity']}): "
                f"{row['occurrence_count']} occurrences"
            )


async def main():
    """
    Main function to run all examples
    الوظيفة الرئيسية لتشغيل جميع الأمثلة
    """
    print("GlobalGAP Compliance Database Examples")
    print("=" * 60)

    try:
        # Initialize database connection
        await init_db()
        print("✓ Database initialized")

        # Run examples
        registration = await example_1_create_registration()
        compliance = await example_2_create_compliance_audit(registration["id"])
        await example_3_add_checklist_responses(compliance["id"])
        nc = await example_4_create_non_conformance(compliance["id"])
        await example_5_query_operations()
        await example_6_update_operations(registration["id"], nc["id"])
        await example_7_transaction_usage(compliance["id"])
        await example_8_health_check()
        await example_9_analytics_queries()

        print("\n" + "=" * 60)
        print("✓ All examples completed successfully")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Close database connection pool
        await close_pool()
        print("✓ Database connection closed")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
