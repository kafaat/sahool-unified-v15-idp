"""Initial Schema - SAHOOL Core Tables
المخطط الأولي - جداول SAHOOL الأساسية

Creates the core database schema including:
- Tenants (المستأجرون)
- Users (المستخدمون)
- Farms (المزارع)
- Fields (الحقول)
- Crops (المحاصيل)
- Sensors (أجهزة الاستشعار)

Revision ID: 001
Revises: None
Create Date: 2026-01-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import datetime

# معرفات المراجعة، تستخدم بواسطة Alembic
# Revision identifiers, used by Alembic
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    ترقية قاعدة البيانات - إنشاء المخطط الأولي
    Upgrade database - Create initial schema
    """

    # =========================================================================
    # جدول المستأجرين / Tenants Table
    # =========================================================================
    op.create_table(
        'tenants',
        # المعرفات / Identity
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False),

        # معلومات المنظمة / Organization Information
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('name_ar', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_ar', sa.Text(), nullable=True),

        # معلومات الاتصال / Contact Information
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('contact_phone', sa.String(50), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),

        # العنوان / Address
        sa.Column('address_line1', sa.String(255), nullable=True),
        sa.Column('address_line2', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('governorate', sa.String(100), nullable=True),  # المحافظة
        sa.Column('country', sa.String(100), default='YE', nullable=False),
        sa.Column('postal_code', sa.String(20), nullable=True),

        # الحالة / Status
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('subscription_tier', sa.String(50), default='basic', nullable=False),

        # البيانات الوصفية / Metadata
        sa.Column('settings', postgresql.JSONB(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),

        # الطوابع الزمنية / Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),
    )

    # فهارس جدول المستأجرين / Tenants table indexes
    op.create_index('ix_tenants_code', 'tenants', ['code'])
    op.create_index('ix_tenants_is_active', 'tenants', ['is_active'])

    # =========================================================================
    # جدول المستخدمين / Users Table
    # =========================================================================
    op.create_table(
        'users',
        # المعرفات / Identity
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),

        # معلومات تسجيل الدخول / Login Information
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),

        # المعلومات الشخصية / Personal Information
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('first_name_ar', sa.String(100), nullable=True),
        sa.Column('last_name_ar', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),

        # الدور والأذونات / Role and Permissions
        sa.Column('role', sa.String(50), default='farmer', nullable=False),
        sa.Column('permissions', postgresql.JSONB(), nullable=True),

        # التفضيلات / Preferences
        sa.Column('language', sa.String(10), default='ar', nullable=False),
        sa.Column('timezone', sa.String(50), default='Asia/Aden', nullable=False),
        sa.Column('preferences', postgresql.JSONB(), nullable=True),

        # الحالة / Status
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),

        # الطوابع الزمنية / Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),

        # المفاتيح الخارجية / Foreign Keys
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'],
                                ondelete='CASCADE'),
    )

    # فهارس جدول المستخدمين / Users table indexes
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_tenant_role', 'users', ['tenant_id', 'role'])

    # =========================================================================
    # جدول المزارع / Farms Table
    # =========================================================================
    op.create_table(
        'farms',
        # المعرفات / Identity
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),

        # المعلومات الأساسية / Basic Information
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('name_ar', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_ar', sa.Text(), nullable=True),

        # الموقع / Location
        sa.Column('governorate', sa.String(100), nullable=False),  # المحافظة
        sa.Column('district', sa.String(100), nullable=True),       # المديرية
        sa.Column('village', sa.String(100), nullable=True),        # القرية
        sa.Column('address', sa.Text(), nullable=True),

        # المساحة / Area
        sa.Column('total_area_hectares', sa.Float(), nullable=False),

        # البيانات الوصفية / Metadata
        sa.Column('metadata', postgresql.JSONB(), nullable=True),

        # الطوابع الزمنية / Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),

        # المفاتيح الخارجية / Foreign Keys
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'],
                                ondelete='RESTRICT'),
    )

    # فهارس جدول المزارع / Farms table indexes
    op.create_index('ix_farms_tenant_id', 'farms', ['tenant_id'])
    op.create_index('ix_farms_owner_id', 'farms', ['owner_id'])
    op.create_index('ix_farms_governorate', 'farms', ['governorate'])

    # =========================================================================
    # جدول الحقول / Fields Table
    # =========================================================================
    op.create_table(
        'fields',
        # المعرفات / Identity
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('farm_id', postgresql.UUID(as_uuid=True), nullable=False),

        # المعلومات الأساسية / Basic Information
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('name_ar', sa.String(200), nullable=True),

        # الحدود والموقع / Boundary and Location
        # سيتم إضافة أعمدة PostGIS في الهجرة 002
        # PostGIS columns will be added in migration 002
        sa.Column('boundary_geojson', postgresql.JSONB(), nullable=True),
        sa.Column('center_latitude', sa.Float(), nullable=True),
        sa.Column('center_longitude', sa.Float(), nullable=True),

        # المساحة / Area
        sa.Column('area_hectares', sa.Float(), nullable=False),

        # نوع التربة / Soil Type
        sa.Column('soil_type', sa.String(50), nullable=False),
        # Possible values: clay, sandy, loamy, silty, peaty, chalky

        # نوع الري / Irrigation Type
        sa.Column('irrigation_type', sa.String(50), nullable=False),
        # Possible values: drip, sprinkler, flood, furrow, rainfed

        # الحالة / Status
        sa.Column('status', sa.String(50), default='active', nullable=False),
        # Possible values: active, fallow, preparation, harvesting

        # المحصول الحالي / Current Crop
        sa.Column('current_crop_id', postgresql.UUID(as_uuid=True), nullable=True),

        # البيانات الوصفية / Metadata
        sa.Column('metadata', postgresql.JSONB(), nullable=True),

        # الطوابع الزمنية / Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),

        # المفاتيح الخارجية / Foreign Keys
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id'],
                                ondelete='CASCADE'),
    )

    # فهارس جدول الحقول / Fields table indexes
    op.create_index('ix_fields_tenant_id', 'fields', ['tenant_id'])
    op.create_index('ix_fields_farm_id', 'fields', ['farm_id'])
    op.create_index('ix_fields_status', 'fields', ['status'])
    op.create_index('ix_fields_tenant_status', 'fields', ['tenant_id', 'status'])

    # =========================================================================
    # جدول المحاصيل / Crops Table
    # =========================================================================
    op.create_table(
        'crops',
        # المعرفات / Identity
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), nullable=False),

        # نوع المحصول / Crop Type
        sa.Column('crop_type', sa.String(100), nullable=False),
        # Possible values: wheat, barley, corn, rice, cotton, coffee, qaat,
        # mango, banana, date_palm, grape, tomato, onion, potato, other

        # الصنف / Variety
        sa.Column('variety', sa.String(100), nullable=True),
        sa.Column('variety_ar', sa.String(100), nullable=True),

        # التواريخ / Dates
        sa.Column('planting_date', sa.Date(), nullable=False),
        sa.Column('expected_harvest_date', sa.Date(), nullable=True),
        sa.Column('actual_harvest_date', sa.Date(), nullable=True),

        # مرحلة النمو / Growth Stage
        sa.Column('growth_stage', sa.String(50), default='planting', nullable=False),
        # Possible values: planting, germination, vegetative, flowering,
        # fruiting, ripening, harvest, post_harvest

        # المحصول / Yield
        sa.Column('yield_estimate_kg', sa.Float(), nullable=True),
        sa.Column('actual_yield_kg', sa.Float(), nullable=True),

        # البيانات الوصفية / Metadata
        sa.Column('metadata', postgresql.JSONB(), nullable=True),

        # الطوابع الزمنية / Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),

        # المفاتيح الخارجية / Foreign Keys
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'],
                                ondelete='CASCADE'),
    )

    # فهارس جدول المحاصيل / Crops table indexes
    op.create_index('ix_crops_tenant_id', 'crops', ['tenant_id'])
    op.create_index('ix_crops_field_id', 'crops', ['field_id'])
    op.create_index('ix_crops_crop_type', 'crops', ['crop_type'])
    op.create_index('ix_crops_growth_stage', 'crops', ['growth_stage'])
    op.create_index('ix_crops_planting_date', 'crops', ['planting_date'])

    # تحديث المفتاح الخارجي للحقل الحالي
    # Update foreign key for current crop in fields table
    op.create_foreign_key(
        'fk_fields_current_crop',
        'fields', 'crops',
        ['current_crop_id'], ['id'],
        ondelete='SET NULL'
    )

    # =========================================================================
    # جدول أجهزة الاستشعار / Sensors Table
    # =========================================================================
    op.create_table(
        'sensors',
        # المعرفات / Identity
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), nullable=False),

        # معلومات الجهاز / Device Information
        sa.Column('device_id', sa.String(100), unique=True, nullable=False),
        sa.Column('device_type', sa.String(50), nullable=False),
        # Possible values: soil_moisture, temperature, humidity, rain_gauge,
        # weather_station, camera, other

        # التكوين / Configuration
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('name_ar', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),

        # الموقع / Location
        # سيتم إضافة أعمدة PostGIS في الهجرة 002
        # PostGIS columns will be added in migration 002
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('altitude', sa.Float(), nullable=True),

        # الحالة / Status
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('battery_level', sa.Float(), nullable=True),

        # البيانات الوصفية / Metadata
        sa.Column('configuration', postgresql.JSONB(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),

        # الطوابع الزمنية / Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),

        # المفاتيح الخارجية / Foreign Keys
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'],
                                ondelete='CASCADE'),
    )

    # فهارس جدول أجهزة الاستشعار / Sensors table indexes
    op.create_index('ix_sensors_tenant_id', 'sensors', ['tenant_id'])
    op.create_index('ix_sensors_field_id', 'sensors', ['field_id'])
    op.create_index('ix_sensors_device_id', 'sensors', ['device_id'])
    op.create_index('ix_sensors_device_type', 'sensors', ['device_type'])
    op.create_index('ix_sensors_is_active', 'sensors', ['is_active'])

    # =========================================================================
    # جدول قراءات الاستشعار / Sensor Readings Table
    # =========================================================================
    op.create_table(
        'sensor_readings',
        # المعرفات / Identity
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('sensor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),

        # البيانات / Data
        sa.Column('reading_type', sa.String(50), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(20), nullable=False),

        # البيانات الإضافية / Additional Data
        sa.Column('additional_data', postgresql.JSONB(), nullable=True),

        # الجودة / Quality
        sa.Column('quality_score', sa.Float(), nullable=True),

        # الطابع الزمني / Timestamp
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),

        # المفاتيح الخارجية / Foreign Keys
        sa.ForeignKeyConstraint(['sensor_id'], ['sensors.id'],
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'],
                                ondelete='CASCADE'),
    )

    # فهارس جدول قراءات الاستشعار / Sensor readings table indexes
    op.create_index('ix_sensor_readings_sensor_id', 'sensor_readings', ['sensor_id'])
    op.create_index('ix_sensor_readings_timestamp', 'sensor_readings', ['timestamp'])
    op.create_index('ix_sensor_readings_sensor_timestamp',
                    'sensor_readings', ['sensor_id', 'timestamp'])
    op.create_index('ix_sensor_readings_reading_type',
                    'sensor_readings', ['reading_type'])

    # =========================================================================
    # جدول تتبع الهجرات / Migrations Tracking Table
    # =========================================================================
    op.create_table(
        'sahool_migrations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('revision', sa.String(64), unique=True, nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('checksum', sa.String(64), nullable=False),
        sa.Column('applied_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('applied_by', sa.String(100), nullable=True),
        sa.Column('is_rollback', sa.Boolean(), default=False, nullable=False),
    )

    op.create_index('ix_sahool_migrations_revision',
                    'sahool_migrations', ['revision'])
    op.create_index('ix_sahool_migrations_applied_at',
                    'sahool_migrations', ['applied_at'])


def downgrade() -> None:
    """
    التراجع عن الترقية - حذف المخطط الأولي
    Downgrade database - Drop initial schema
    """

    # حذف الجداول بترتيب عكسي (بسبب المفاتيح الخارجية)
    # Drop tables in reverse order (due to foreign keys)

    # جدول قراءات الاستشعار / Sensor Readings Table
    op.drop_index('ix_sensor_readings_reading_type', table_name='sensor_readings')
    op.drop_index('ix_sensor_readings_sensor_timestamp', table_name='sensor_readings')
    op.drop_index('ix_sensor_readings_timestamp', table_name='sensor_readings')
    op.drop_index('ix_sensor_readings_sensor_id', table_name='sensor_readings')
    op.drop_table('sensor_readings')

    # جدول أجهزة الاستشعار / Sensors Table
    op.drop_index('ix_sensors_is_active', table_name='sensors')
    op.drop_index('ix_sensors_device_type', table_name='sensors')
    op.drop_index('ix_sensors_device_id', table_name='sensors')
    op.drop_index('ix_sensors_field_id', table_name='sensors')
    op.drop_index('ix_sensors_tenant_id', table_name='sensors')
    op.drop_table('sensors')

    # حذف المفتاح الخارجي للمحصول الحالي
    # Drop foreign key for current crop
    op.drop_constraint('fk_fields_current_crop', 'fields', type_='foreignkey')

    # جدول المحاصيل / Crops Table
    op.drop_index('ix_crops_planting_date', table_name='crops')
    op.drop_index('ix_crops_growth_stage', table_name='crops')
    op.drop_index('ix_crops_crop_type', table_name='crops')
    op.drop_index('ix_crops_field_id', table_name='crops')
    op.drop_index('ix_crops_tenant_id', table_name='crops')
    op.drop_table('crops')

    # جدول الحقول / Fields Table
    op.drop_index('ix_fields_tenant_status', table_name='fields')
    op.drop_index('ix_fields_status', table_name='fields')
    op.drop_index('ix_fields_farm_id', table_name='fields')
    op.drop_index('ix_fields_tenant_id', table_name='fields')
    op.drop_table('fields')

    # جدول المزارع / Farms Table
    op.drop_index('ix_farms_governorate', table_name='farms')
    op.drop_index('ix_farms_owner_id', table_name='farms')
    op.drop_index('ix_farms_tenant_id', table_name='farms')
    op.drop_table('farms')

    # جدول المستخدمين / Users Table
    op.drop_index('ix_users_tenant_role', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_tenant_id', table_name='users')
    op.drop_table('users')

    # جدول المستأجرين / Tenants Table
    op.drop_index('ix_tenants_is_active', table_name='tenants')
    op.drop_index('ix_tenants_code', table_name='tenants')
    op.drop_table('tenants')

    # جدول تتبع الهجرات / Migrations Tracking Table
    op.drop_index('ix_sahool_migrations_applied_at', table_name='sahool_migrations')
    op.drop_index('ix_sahool_migrations_revision', table_name='sahool_migrations')
    op.drop_table('sahool_migrations')
