#!/usr/bin/env python3
"""
SAHOOL Notification Service - Farmer Profile Repository Usage Examples
أمثلة استخدام مستودع ملفات المزارعين

This file demonstrates how to use the FarmerProfileRepository to manage farmer data.
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from repository import FarmerProfileRepository

from database import close_db, init_db


async def example_create_farmer():
    """Example: Create a new farmer profile"""
    print("\n" + "=" * 60)
    print("Example 1: Create a new farmer profile")
    print("=" * 60)

    farmer = await FarmerProfileRepository.create(
        farmer_id="farmer-001",
        name="Ali Mohammed",
        name_ar="علي محمد",
        governorate="sanaa",
        district="Bani Harith",
        crops=["tomato", "coffee", "wheat"],
        field_ids=["field-101", "field-102"],
        phone="+967771234567",
        email="ali.mohammed@example.com",
        fcm_token="fcm-token-123456",
        language="ar",
    )

    print(f"✅ Created farmer: {farmer.farmer_id}")
    print(f"   Name (AR): {farmer.name_ar}")
    print(f"   Governorate: {farmer.governorate}")
    print(f"   Phone: {farmer.phone}")


async def example_get_farmer():
    """Example: Retrieve a farmer profile"""
    print("\n" + "=" * 60)
    print("Example 2: Retrieve a farmer profile")
    print("=" * 60)

    farmer = await FarmerProfileRepository.get_by_farmer_id("farmer-001")

    if farmer:
        print(f"✅ Found farmer: {farmer.farmer_id}")
        print(f"   Name: {farmer.name}")
        print(f"   Name (AR): {farmer.name_ar}")
        print(f"   Governorate: {farmer.governorate}")
        print(f"   District: {farmer.district}")
        print(f"   Phone: {farmer.phone}")
        print(f"   Email: {farmer.email}")
        print(f"   Language: {farmer.language}")

        # Get crops
        crops = await FarmerProfileRepository.get_farmer_crops("farmer-001")
        print(f"   Crops: {', '.join(crops)}")

        # Get fields
        fields = await FarmerProfileRepository.get_farmer_fields("farmer-001")
        print(f"   Fields: {', '.join(fields)}")
    else:
        print("❌ Farmer not found")


async def example_update_farmer():
    """Example: Update a farmer profile"""
    print("\n" + "=" * 60)
    print("Example 3: Update a farmer profile")
    print("=" * 60)

    farmer = await FarmerProfileRepository.update(
        farmer_id="farmer-001",
        phone="+967779999999",  # Update phone
        crops=["tomato", "coffee", "banana"],  # Update crops (removed wheat, added banana)
        email="ali.new@example.com",  # Update email
    )

    print(f"✅ Updated farmer: {farmer.farmer_id}")
    print(f"   New phone: {farmer.phone}")
    print(f"   New email: {farmer.email}")

    # Get updated crops
    crops = await FarmerProfileRepository.get_farmer_crops("farmer-001")
    print(f"   Updated crops: {', '.join(crops)}")


async def example_find_farmers_by_criteria():
    """Example: Find farmers by governorate and crops"""
    print("\n" + "=" * 60)
    print("Example 4: Find farmers by criteria")
    print("=" * 60)

    # Find all farmers in Sanaa
    farmers = await FarmerProfileRepository.find_by_criteria(
        governorates=["sanaa"],
    )
    print(f"\n✅ Found {len(farmers)} farmers in Sanaa")
    for farmer in farmers:
        print(f"   - {farmer.farmer_id}: {farmer.name_ar}")

    # Find all farmers growing tomatoes
    farmers = await FarmerProfileRepository.find_by_criteria(
        crops=["tomato"],
    )
    print(f"\n✅ Found {len(farmers)} farmers growing tomatoes")
    for farmer in farmers:
        crops = await FarmerProfileRepository.get_farmer_crops(farmer.farmer_id)
        print(f"   - {farmer.farmer_id}: {farmer.name_ar} (crops: {', '.join(crops)})")

    # Find farmers in Sanaa growing coffee
    farmers = await FarmerProfileRepository.find_by_criteria(
        governorates=["sanaa"],
        crops=["coffee"],
    )
    print(f"\n✅ Found {len(farmers)} farmers in Sanaa growing coffee")
    for farmer in farmers:
        print(f"   - {farmer.farmer_id}: {farmer.name_ar}")


async def example_get_all_farmers():
    """Example: Get all farmers with pagination"""
    print("\n" + "=" * 60)
    print("Example 5: Get all farmers (paginated)")
    print("=" * 60)

    # Get total count
    count = await FarmerProfileRepository.get_count()
    print(f"Total farmers: {count}")

    # Get first page (10 farmers)
    farmers = await FarmerProfileRepository.get_all(limit=10, offset=0)
    print(f"\n✅ Retrieved {len(farmers)} farmers (page 1)")
    for farmer in farmers:
        print(f"   - {farmer.farmer_id}: {farmer.name_ar} ({farmer.governorate})")


async def example_create_multiple_farmers():
    """Example: Create multiple farmers for testing"""
    print("\n" + "=" * 60)
    print("Example 6: Create multiple farmers")
    print("=" * 60)

    farmers_data = [
        {
            "farmer_id": "farmer-002",
            "name": "Fatima Ali",
            "name_ar": "فاطمة علي",
            "governorate": "ibb",
            "crops": ["banana", "mango"],
            "field_ids": ["field-201"],
            "phone": "+967772222222",
        },
        {
            "farmer_id": "farmer-003",
            "name": "Hassan Ahmed",
            "name_ar": "حسن أحمد",
            "governorate": "taiz",
            "crops": ["wheat", "corn"],
            "field_ids": ["field-301", "field-302"],
            "phone": "+967773333333",
        },
        {
            "farmer_id": "farmer-004",
            "name": "Nadia Mohammed",
            "name_ar": "نادية محمد",
            "governorate": "sanaa",
            "crops": ["tomato", "potato"],
            "field_ids": ["field-401"],
            "email": "nadia@example.com",
        },
    ]

    for data in farmers_data:
        try:
            farmer = await FarmerProfileRepository.create(**data)
            print(f"✅ Created: {farmer.farmer_id} - {farmer.name_ar}")
        except Exception as e:
            print(f"⚠️  Skipped {data['farmer_id']}: {e}")


async def example_delete_farmer():
    """Example: Delete a farmer profile"""
    print("\n" + "=" * 60)
    print("Example 7: Delete a farmer profile")
    print("=" * 60)

    # Create a test farmer to delete
    await FarmerProfileRepository.create(
        farmer_id="farmer-temp",
        name="Temp User",
        name_ar="مستخدم مؤقت",
        governorate="aden",
        crops=["qat"],
        field_ids=["field-temp"],
    )
    print("✅ Created temporary farmer: farmer-temp")

    # Delete the farmer
    success = await FarmerProfileRepository.delete("farmer-temp")
    if success:
        print("✅ Deleted farmer: farmer-temp")
    else:
        print("❌ Failed to delete farmer")

    # Verify deletion
    farmer = await FarmerProfileRepository.get_by_farmer_id("farmer-temp")
    if farmer is None:
        print("✅ Verified: farmer no longer exists")


async def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("SAHOOL Farmer Profile Repository - Usage Examples")
    print("أمثلة استخدام مستودع ملفات المزارعين")
    print("=" * 80)

    # Initialize database
    print("\n📊 Initializing database...")
    await init_db(create_db=False)  # Don't recreate schema
    print("✅ Database initialized")

    try:
        # Run examples
        await example_create_farmer()
        await example_get_farmer()
        await example_update_farmer()
        await example_create_multiple_farmers()
        await example_get_all_farmers()
        await example_find_farmers_by_criteria()
        await example_delete_farmer()

        print("\n" + "=" * 80)
        print("✅ All examples completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Close database
        print("\n🔌 Closing database connection...")
        await close_db()
        print("✅ Database connection closed")


if __name__ == "__main__":
    # Check DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("   Set it in .env or export it:")
        print(
            "   export DATABASE_URL='postgresql://user:password@localhost:5432/sahool_notifications'"
        )
        sys.exit(1)

    # Run examples
    asyncio.run(run_all_examples())
