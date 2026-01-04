"""
SAHOOL Development Environment Seeder
تعبئة بيئة التطوير

Seeds the database with sample data for development and testing.
تعبئة قاعدة البيانات ببيانات نموذجية للتطوير والاختبار.
"""

import uuid
from datetime import datetime, timedelta, date
from typing import Dict, Any, List
import random

from sqlalchemy import text
from sqlalchemy.orm import Session

from . import BaseSeeder


class DevelopmentSeeder(BaseSeeder):
    """
    تعبئة بيانات التطوير
    Development Data Seeder

    Seeds the database with sample data representing farms in Yemen.
    تعبئة قاعدة البيانات ببيانات نموذجية تمثل مزارع في اليمن.
    """

    def seed(self) -> Dict[str, Any]:
        """
        تعبئة قاعدة البيانات ببيانات التطوير
        Seed database with development data
        """
        start_time = datetime.utcnow()
        results = {
            "success": True,
            "tenants": 0,
            "users": 0,
            "farms": 0,
            "fields": 0,
            "crops": 0,
            "sensors": 0,
        }

        self._log("Starting development data seeding...", "بدء تعبئة بيانات التطوير...")

        with Session(self.engine) as session:
            try:
                # تعبئة المستأجرين / Seed tenants
                tenants = self._seed_tenants(session)
                results["tenants"] = len(tenants)

                # تعبئة المستخدمين / Seed users
                users = self._seed_users(session, tenants)
                results["users"] = len(users)

                # تعبئة المزارع / Seed farms
                farms = self._seed_farms(session, tenants, users)
                results["farms"] = len(farms)

                # تعبئة الحقول / Seed fields
                fields = self._seed_fields(session, tenants, farms)
                results["fields"] = len(fields)

                # تعبئة المحاصيل / Seed crops
                crops = self._seed_crops(session, tenants, fields)
                results["crops"] = len(crops)

                # تعبئة أجهزة الاستشعار / Seed sensors
                sensors = self._seed_sensors(session, tenants, fields)
                results["sensors"] = len(sensors)

                # تنفيذ جميع التغييرات / Commit all changes
                session.commit()

                end_time = datetime.utcnow()
                results["execution_time_ms"] = (
                    end_time - start_time
                ).total_seconds() * 1000

                self._log(
                    "Development data seeding completed successfully!",
                    "اكتملت تعبئة بيانات التطوير بنجاح!",
                )
                self._log(
                    f"Created: {results['tenants']} tenants, {results['users']} users, "
                    f"{results['farms']} farms, {results['fields']} fields, "
                    f"{results['crops']} crops, {results['sensors']} sensors",
                    f"تم إنشاء: {results['tenants']} مستأجر، {results['users']} مستخدم، "
                    f"{results['farms']} مزرعة، {results['fields']} حقل، "
                    f"{results['crops']} محصول، {results['sensors']} جهاز استشعار",
                )

            except Exception as e:
                session.rollback()
                results["success"] = False
                results["error"] = str(e)
                self._log(
                    f"Error during seeding: {str(e)}", f"خطأ أثناء التعبئة: {str(e)}"
                )

        return results

    def _seed_tenants(self, session: Session) -> List[Dict]:
        """
        تعبئة المستأجرين
        Seed tenants
        """
        self._log("Seeding tenants...", "تعبئة المستأجرين...")

        tenants = [
            {
                "id": uuid.uuid4(),
                "code": "yemen-agro",
                "name": "Yemen Agricultural Cooperative",
                "name_ar": "التعاونية الزراعية اليمنية",
                "description": "Leading agricultural cooperative in Yemen",
                "description_ar": "التعاونية الزراعية الرائدة في اليمن",
                "contact_email": "info@yemen-agro.ye",
                "contact_phone": "+967-1-234567",
                "governorate": "Sana'a",
                "country": "YE",
                "is_active": True,
                "subscription_tier": "premium",
            },
            {
                "id": uuid.uuid4(),
                "code": "taiz-farmers",
                "name": "Taiz Farmers Union",
                "name_ar": "اتحاد مزارعي تعز",
                "description": "Farmers union serving Taiz region",
                "description_ar": "اتحاد المزارعين الذي يخدم منطقة تعز",
                "contact_email": "contact@taiz-farmers.ye",
                "contact_phone": "+967-4-567890",
                "governorate": "Taiz",
                "country": "YE",
                "is_active": True,
                "subscription_tier": "standard",
            },
        ]

        for tenant_data in tenants:
            session.execute(
                text(
                    """
                    INSERT INTO tenants (
                        id, code, name, name_ar, description, description_ar,
                        contact_email, contact_phone, governorate, country,
                        is_active, subscription_tier, created_at, updated_at
                    ) VALUES (
                        :id, :code, :name, :name_ar, :description, :description_ar,
                        :contact_email, :contact_phone, :governorate, :country,
                        :is_active, :subscription_tier, NOW(), NOW()
                    )
                """
                ),
                tenant_data,
            )

        return tenants

    def _seed_users(self, session: Session, tenants: List[Dict]) -> List[Dict]:
        """
        تعبئة المستخدمين
        Seed users
        """
        self._log("Seeding users...", "تعبئة المستخدمين...")

        users = []

        # مستخدمون لكل مستأجر / Users for each tenant
        for tenant in tenants:
            tenant_users = [
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant["id"],
                    "username": f"admin_{tenant['code']}",
                    "email": f"admin@{tenant['code']}.ye",
                    "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyJ3DUX.Sq2.",  # "password123"
                    "first_name": "Administrator",
                    "last_name": "User",
                    "first_name_ar": "مدير",
                    "last_name_ar": "النظام",
                    "phone": "+967-777-123456",
                    "role": "admin",
                    "language": "ar",
                    "timezone": "Asia/Aden",
                    "is_active": True,
                    "is_verified": True,
                },
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant["id"],
                    "username": f"farmer_{tenant['code']}",
                    "email": f"farmer@{tenant['code']}.ye",
                    "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyJ3DUX.Sq2.",
                    "first_name": "Ahmed",
                    "last_name": "Al-Yamani",
                    "first_name_ar": "أحمد",
                    "last_name_ar": "اليماني",
                    "phone": "+967-777-234567",
                    "role": "farmer",
                    "language": "ar",
                    "timezone": "Asia/Aden",
                    "is_active": True,
                    "is_verified": True,
                },
            ]

            for user_data in tenant_users:
                session.execute(
                    text(
                        """
                        INSERT INTO users (
                            id, tenant_id, username, email, password_hash,
                            first_name, last_name, first_name_ar, last_name_ar,
                            phone, role, language, timezone,
                            is_active, is_verified, created_at, updated_at
                        ) VALUES (
                            :id, :tenant_id, :username, :email, :password_hash,
                            :first_name, :last_name, :first_name_ar, :last_name_ar,
                            :phone, :role, :language, :timezone,
                            :is_active, :is_verified, NOW(), NOW()
                        )
                    """
                    ),
                    user_data,
                )
                users.append(user_data)

        return users

    def _seed_farms(
        self, session: Session, tenants: List[Dict], users: List[Dict]
    ) -> List[Dict]:
        """
        تعبئة المزارع
        Seed farms
        """
        self._log("Seeding farms...", "تعبئة المزارع...")

        farms = []

        # مزارع في محافظات مختلفة باليمن
        # Farms in different governorates in Yemen
        farm_templates = [
            {
                "name": "Green Valley Farm",
                "name_ar": "مزرعة الوادي الأخضر",
                "governorate": "Sana'a",
                "district": "Bani Hushaysh",
                "village": "Al-Rawdah",
                "total_area_hectares": 15.5,
            },
            {
                "name": "Al-Bustan Agricultural Farm",
                "name_ar": "مزرعة البستان الزراعية",
                "governorate": "Taiz",
                "district": "Maqbanah",
                "village": "Wadi Al-Qamh",
                "total_area_hectares": 22.3,
            },
            {
                "name": "Tihama Coffee Estate",
                "name_ar": "مزرعة تهامة للبن",
                "governorate": "Al Hudaydah",
                "district": "Bajil",
                "village": "Al-Mansuriyah",
                "total_area_hectares": 18.7,
            },
        ]

        for tenant in tenants:
            # العثور على مزارع لهذا المستأجر / Find farmers for this tenant
            tenant_farmers = [
                u
                for u in users
                if u["tenant_id"] == tenant["id"] and u["role"] == "farmer"
            ]

            for i, farm_template in enumerate(farm_templates):
                if i < len(tenant_farmers):
                    farm_data = {
                        "id": uuid.uuid4(),
                        "tenant_id": tenant["id"],
                        "owner_id": tenant_farmers[i]["id"],
                        **farm_template,
                    }
                    session.execute(
                        text(
                            """
                            INSERT INTO farms (
                                id, tenant_id, owner_id, name, name_ar,
                                governorate, district, village, total_area_hectares,
                                created_at, updated_at
                            ) VALUES (
                                :id, :tenant_id, :owner_id, :name, :name_ar,
                                :governorate, :district, :village, :total_area_hectares,
                                NOW(), NOW()
                            )
                        """
                        ),
                        farm_data,
                    )
                    farms.append(farm_data)

        return farms

    def _seed_fields(
        self, session: Session, tenants: List[Dict], farms: List[Dict]
    ) -> List[Dict]:
        """
        تعبئة الحقول
        Seed fields with Yemen locations
        """
        self._log("Seeding fields...", "تعبئة الحقول...")

        fields = []

        # إحداثيات نموذجية في اليمن
        # Sample coordinates in Yemen
        yemen_locations = [
            # صنعاء / Sana'a
            {"lat": 15.3694, "lon": 44.1910, "name": "Field A", "name_ar": "الحقل أ"},
            {"lat": 15.3550, "lon": 44.2075, "name": "Field B", "name_ar": "الحقل ب"},
            # تعز / Taiz
            {"lat": 13.5795, "lon": 44.0165, "name": "Field C", "name_ar": "الحقل ج"},
            {"lat": 13.6000, "lon": 44.0300, "name": "Field D", "name_ar": "الحقل د"},
            # الحديدة / Al Hudaydah
            {"lat": 14.7978, "lon": 42.9545, "name": "Field E", "name_ar": "الحقل هـ"},
        ]

        soil_types = ["clay", "sandy", "loamy", "silty"]
        irrigation_types = ["drip", "sprinkler", "flood", "rainfed"]

        for farm in farms:
            # إنشاء 2-3 حقول لكل مزرعة / Create 2-3 fields per farm
            num_fields = random.randint(2, 3)

            for i in range(num_fields):
                location = random.choice(yemen_locations)

                # إنشاء حدود بسيطة حول النقطة المركزية
                # Create simple boundary around center point
                offset = 0.005  # حوالي 500 متر / About 500 meters
                boundary = {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [location["lon"] - offset, location["lat"] - offset],
                            [location["lon"] + offset, location["lat"] - offset],
                            [location["lon"] + offset, location["lat"] + offset],
                            [location["lon"] - offset, location["lat"] + offset],
                            [location["lon"] - offset, location["lat"] - offset],
                        ]
                    ],
                }

                field_data = {
                    "id": uuid.uuid4(),
                    "tenant_id": farm["tenant_id"],
                    "farm_id": farm["id"],
                    "name": f"{location['name']} {i+1}",
                    "name_ar": f"{location['name_ar']} {i+1}",
                    "center_latitude": location["lat"],
                    "center_longitude": location["lon"],
                    "area_hectares": round(random.uniform(2.0, 8.0), 2),
                    "soil_type": random.choice(soil_types),
                    "irrigation_type": random.choice(irrigation_types),
                    "status": "active",
                }

                session.execute(
                    text(
                        """
                        INSERT INTO fields (
                            id, tenant_id, farm_id, name, name_ar,
                            center_latitude, center_longitude, area_hectares,
                            soil_type, irrigation_type, status,
                            created_at, updated_at
                        ) VALUES (
                            :id, :tenant_id, :farm_id, :name, :name_ar,
                            :center_latitude, :center_longitude, :area_hectares,
                            :soil_type, :irrigation_type, :status,
                            NOW(), NOW()
                        )
                    """
                    ),
                    field_data,
                )
                fields.append(field_data)

        return fields

    def _seed_crops(
        self, session: Session, tenants: List[Dict], fields: List[Dict]
    ) -> List[Dict]:
        """
        تعبئة المحاصيل
        Seed crops
        """
        self._log("Seeding crops...", "تعبئة المحاصيل...")

        crops = []

        # محاصيل شائعة في اليمن / Common crops in Yemen
        crop_types = [
            {
                "type": "wheat",
                "variety": "Yemen Red",
                "variety_ar": "القمح اليمني الأحمر",
            },
            {
                "type": "coffee",
                "variety": "Yemen Mokha",
                "variety_ar": "البن اليمني المخا",
            },
            {"type": "qaat", "variety": "Wadi Hadramaut", "variety_ar": "وادي حضرموت"},
            {"type": "mango", "variety": "Alphonso", "variety_ar": "ألفونسو"},
            {"type": "date_palm", "variety": "Medjool", "variety_ar": "المجهول"},
            {"type": "tomato", "variety": "Roma", "variety_ar": "روما"},
        ]

        growth_stages = [
            "planting",
            "germination",
            "vegetative",
            "flowering",
            "fruiting",
        ]

        for field in fields:
            # حوالي 70% من الحقول لديها محاصيل / About 70% of fields have crops
            if random.random() < 0.7:
                crop_template = random.choice(crop_types)

                planting_date = date.today() - timedelta(days=random.randint(30, 180))
                expected_harvest = planting_date + timedelta(
                    days=random.randint(90, 180)
                )

                crop_data = {
                    "id": uuid.uuid4(),
                    "tenant_id": field["tenant_id"],
                    "field_id": field["id"],
                    "crop_type": crop_template["type"],
                    "variety": crop_template["variety"],
                    "variety_ar": crop_template["variety_ar"],
                    "planting_date": planting_date,
                    "expected_harvest_date": expected_harvest,
                    "growth_stage": random.choice(growth_stages),
                    "yield_estimate_kg": round(random.uniform(500, 5000), 2),
                }

                session.execute(
                    text(
                        """
                        INSERT INTO crops (
                            id, tenant_id, field_id, crop_type, variety, variety_ar,
                            planting_date, expected_harvest_date, growth_stage,
                            yield_estimate_kg, created_at, updated_at
                        ) VALUES (
                            :id, :tenant_id, :field_id, :crop_type, :variety, :variety_ar,
                            :planting_date, :expected_harvest_date, :growth_stage,
                            :yield_estimate_kg, NOW(), NOW()
                        )
                    """
                    ),
                    crop_data,
                )
                crops.append(crop_data)

                # تحديث current_crop_id في الحقل / Update current_crop_id in field
                session.execute(
                    text(
                        "UPDATE fields SET current_crop_id = :crop_id WHERE id = :field_id"
                    ),
                    {"crop_id": crop_data["id"], "field_id": field["id"]},
                )

        return crops

    def _seed_sensors(
        self, session: Session, tenants: List[Dict], fields: List[Dict]
    ) -> List[Dict]:
        """
        تعبئة أجهزة الاستشعار
        Seed sensors
        """
        self._log("Seeding sensors...", "تعبئة أجهزة الاستشعار...")

        sensors = []

        device_types = [
            {
                "type": "soil_moisture",
                "name": "Soil Moisture Sensor",
                "name_ar": "مستشعر رطوبة التربة",
            },
            {
                "type": "temperature",
                "name": "Temperature Sensor",
                "name_ar": "مستشعر درجة الحرارة",
            },
            {
                "type": "humidity",
                "name": "Humidity Sensor",
                "name_ar": "مستشعر الرطوبة",
            },
            {
                "type": "weather_station",
                "name": "Weather Station",
                "name_ar": "محطة الطقس",
            },
        ]

        for field in fields:
            # حوالي 50% من الحقول لديها أجهزة استشعار / About 50% of fields have sensors
            if random.random() < 0.5:
                num_sensors = random.randint(1, 2)

                for i in range(num_sensors):
                    device = random.choice(device_types)

                    # موقع قريب من مركز الحقل / Location near field center
                    lat_offset = random.uniform(-0.001, 0.001)
                    lon_offset = random.uniform(-0.001, 0.001)

                    sensor_data = {
                        "id": uuid.uuid4(),
                        "tenant_id": field["tenant_id"],
                        "field_id": field["id"],
                        "device_id": f"SENSOR-{uuid.uuid4().hex[:8].upper()}",
                        "device_type": device["type"],
                        "name": f"{device['name']} {i+1}",
                        "name_ar": f"{device['name_ar']} {i+1}",
                        "latitude": field["center_latitude"] + lat_offset,
                        "longitude": field["center_longitude"] + lon_offset,
                        "is_active": True,
                        "battery_level": round(random.uniform(60, 100), 1),
                    }

                    session.execute(
                        text(
                            """
                            INSERT INTO sensors (
                                id, tenant_id, field_id, device_id, device_type,
                                name, name_ar, latitude, longitude,
                                is_active, battery_level, last_seen,
                                created_at, updated_at
                            ) VALUES (
                                :id, :tenant_id, :field_id, :device_id, :device_type,
                                :name, :name_ar, :latitude, :longitude,
                                :is_active, :battery_level, NOW(),
                                NOW(), NOW()
                            )
                        """
                        ),
                        sensor_data,
                    )
                    sensors.append(sensor_data)

        return sensors
