/**
 * SAHOOL Field Management Service - Database Seeding
 * خدمة إدارة الحقول - بذر قاعدة البيانات
 *
 * This script populates the database with sample data for development and testing.
 * هذا السكريبت يملأ قاعدة البيانات ببيانات عينة للتطوير والاختبار.
 *
 * Usage: npx prisma db seed
 */

import { PrismaClient, FieldStatus, TaskType, Priority, TaskState } from '@prisma/client';

const prisma = new PrismaClient();

// Sample tenant IDs
// معرفات المستأجرين العينة
const TENANTS = {
  DEMO: 'tenant-demo-001',
  TEST: 'tenant-test-001',
  DEV: 'tenant-dev-001',
};

// Sample crop types
// أنواع المحاصيل العينة
const CROP_TYPES = [
  'wheat',     // قمح
  'barley',    // شعير
  'date_palm', // نخيل التمر
  'tomato',    // طماطم
  'cucumber',  // خيار
  'alfalfa',   // برسيم
  'cotton',    // قطن
  'corn',      // ذرة
];

// Sample irrigation types
// أنواع الري العينة
const IRRIGATION_TYPES = ['drip', 'sprinkler', 'flood', 'pivot'];

// Sample soil types
// أنواع التربة العينة
const SOIL_TYPES = ['sandy', 'clay', 'loamy', 'silty', 'peaty'];

/**
 * Generate a random farm
 * توليد مزرعة عشوائية
 */
async function createFarm(tenantId: string, index: number) {
  const farmNames = [
    { en: 'Al-Rashid Farm', ar: 'مزرعة الراشد' },
    { en: 'Green Valley Farm', ar: 'مزرعة الوادي الأخضر' },
    { en: 'Al-Noor Agricultural', ar: 'الزراعية النور' },
    { en: 'Al-Baraka Farm', ar: 'مزرعة البركة' },
    { en: 'Al-Firdaus Farm', ar: 'مزرعة الفردوس' },
  ];

  const farm = farmNames[index % farmNames.length];

  return prisma.$executeRaw`
    INSERT INTO farms (id, name, tenant_id, total_area_hectares, address, is_deleted, created_at, updated_at)
    VALUES (
      gen_random_uuid(),
      ${farm.en},
      ${tenantId},
      ${(Math.random() * 100 + 10).toFixed(2)}::decimal,
      ${'Sample Address ' + (index + 1)},
      false,
      NOW(),
      NOW()
    )
    RETURNING id
  `;
}

/**
 * Generate sample fields
 * توليد حقول عينة
 */
async function createFields(tenantId: string, farmId: string | null, count: number) {
  const fields = [];

  for (let i = 0; i < count; i++) {
    const cropType = CROP_TYPES[Math.floor(Math.random() * CROP_TYPES.length)];
    const irrigationType = IRRIGATION_TYPES[Math.floor(Math.random() * IRRIGATION_TYPES.length)];
    const soilType = SOIL_TYPES[Math.floor(Math.random() * SOIL_TYPES.length)];
    const status: FieldStatus = ['active', 'fallow', 'harvested', 'preparing'][
      Math.floor(Math.random() * 4)
    ] as FieldStatus;

    // Generate random coordinates in Saudi Arabia region
    const lat = 24.5 + Math.random() * 3; // Approx Saudi Arabia latitude
    const lng = 46.5 + Math.random() * 2; // Approx Saudi Arabia longitude

    const field = await prisma.field.create({
      data: {
        name: `Field ${String(i + 1).padStart(3, '0')} - ${cropType}`,
        tenantId,
        cropType,
        farmId,
        areaHectares: parseFloat((Math.random() * 50 + 1).toFixed(4)),
        healthScore: parseFloat((Math.random() * 0.4 + 0.6).toFixed(2)), // 0.6 - 1.0
        ndviValue: parseFloat((Math.random() * 0.5 + 0.3).toFixed(3)), // 0.3 - 0.8
        status,
        irrigationType,
        soilType,
        plantingDate: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000), // Last 90 days
        expectedHarvest: new Date(Date.now() + Math.random() * 120 * 24 * 60 * 60 * 1000), // Next 120 days
        metadata: {
          notes: `Sample field for ${cropType} cultivation`,
          notes_ar: `حقل عينة لزراعة ${cropType}`,
          lat,
          lng,
        },
      },
    });

    fields.push(field);
  }

  return fields;
}

/**
 * Generate sample tasks
 * توليد مهام عينة
 */
async function createTasks(fieldIds: string[], tenantId: string) {
  const taskTemplates = [
    { title: 'Irrigation Check', titleAr: 'فحص الري', type: TaskType.irrigation },
    { title: 'Apply Fertilizer', titleAr: 'تطبيق السماد', type: TaskType.fertilization },
    { title: 'Pest Inspection', titleAr: 'فحص الآفات', type: TaskType.scouting },
    { title: 'Spray Treatment', titleAr: 'معالجة الرش', type: TaskType.spraying },
    { title: 'Harvest Preparation', titleAr: 'تحضير الحصاد', type: TaskType.harvest },
    { title: 'Soil Sampling', titleAr: 'أخذ عينات التربة', type: TaskType.sampling },
    { title: 'Equipment Maintenance', titleAr: 'صيانة المعدات', type: TaskType.maintenance },
    { title: 'Planting Seeds', titleAr: 'زراعة البذور', type: TaskType.planting },
  ];

  const priorities: Priority[] = [Priority.low, Priority.medium, Priority.high, Priority.urgent];
  const statuses: TaskState[] = [TaskState.pending, TaskState.in_progress, TaskState.completed];

  for (const fieldId of fieldIds) {
    // Create 2-4 tasks per field
    const taskCount = Math.floor(Math.random() * 3) + 2;

    for (let i = 0; i < taskCount; i++) {
      const template = taskTemplates[Math.floor(Math.random() * taskTemplates.length)];
      const priority = priorities[Math.floor(Math.random() * priorities.length)];
      const status = statuses[Math.floor(Math.random() * statuses.length)];

      await prisma.task.create({
        data: {
          title: template.title,
          titleAr: template.titleAr,
          description: `${template.title} task for field maintenance and monitoring.`,
          taskType: template.type,
          priority,
          status,
          dueDate: new Date(Date.now() + Math.random() * 14 * 24 * 60 * 60 * 1000), // Next 14 days
          createdBy: 'seed-script',
          fieldId,
          estimatedMinutes: Math.floor(Math.random() * 120) + 30, // 30-150 minutes
          completedAt: status === TaskState.completed ? new Date() : null,
        },
      });
    }
  }
}

/**
 * Generate sample NDVI readings
 * توليد قراءات NDVI عينة
 */
async function createNdviReadings(fieldIds: string[]) {
  const sources = ['satellite', 'drone', 'manual'];
  const qualities = ['good', 'moderate', 'poor'];
  const satellites = ['Sentinel-2', 'Landsat-8', 'Planet'];

  for (const fieldId of fieldIds) {
    // Create 5-10 NDVI readings per field (historical data)
    const readingCount = Math.floor(Math.random() * 6) + 5;

    for (let i = 0; i < readingCount; i++) {
      const source = sources[Math.floor(Math.random() * sources.length)];

      await prisma.ndviReading.create({
        data: {
          fieldId,
          value: parseFloat((Math.random() * 0.6 + 0.2).toFixed(3)), // 0.2 - 0.8
          capturedAt: new Date(Date.now() - i * 7 * 24 * 60 * 60 * 1000), // Weekly readings
          source,
          cloudCover: source === 'satellite' ? parseFloat((Math.random() * 30).toFixed(2)) : null,
          quality: qualities[Math.floor(Math.random() * qualities.length)],
          satelliteName: source === 'satellite' ? satellites[Math.floor(Math.random() * satellites.length)] : null,
          bandInfo: source === 'satellite' ? {
            red: 'B04',
            nir: 'B08',
            resolution: '10m',
          } : null,
        },
      });
    }
  }
}

/**
 * Main seeding function
 * دالة البذر الرئيسية
 */
async function main() {
  console.log('🌱 Starting database seeding...');
  console.log('🌱 بدء بذر قاعدة البيانات...');

  // Clear existing data (optional - comment out for incremental seeding)
  console.log('🗑️ Clearing existing data...');
  await prisma.ndviReading.deleteMany();
  await prisma.task.deleteMany();
  await prisma.fieldBoundaryHistory.deleteMany();
  await prisma.field.deleteMany();
  await prisma.syncStatus.deleteMany();
  // Note: Farms need raw SQL due to PostGIS geometry types
  await prisma.$executeRaw`DELETE FROM farms`;

  // Create farms for each tenant
  console.log('🏠 Creating farms...');
  for (const [tenantName, tenantId] of Object.entries(TENANTS)) {
    console.log(`  - Creating farms for ${tenantName} (${tenantId})`);
    for (let i = 0; i < 3; i++) {
      await createFarm(tenantId, i);
    }
  }

  // Get all farms
  const farms = await prisma.$queryRaw<{ id: string; tenant_id: string }[]>`
    SELECT id, tenant_id FROM farms
  `;

  // Create fields for each farm
  console.log('🌾 Creating fields...');
  const allFieldIds: string[] = [];
  for (const farm of farms) {
    const fieldCount = Math.floor(Math.random() * 5) + 3; // 3-7 fields per farm
    const fields = await createFields(farm.tenant_id, farm.id, fieldCount);
    allFieldIds.push(...fields.map(f => f.id));
    console.log(`  - Created ${fieldCount} fields for farm ${farm.id.substring(0, 8)}...`);
  }

  // Create standalone fields (no farm association)
  console.log('🌿 Creating standalone fields...');
  for (const tenantId of Object.values(TENANTS)) {
    const standaloneFields = await createFields(tenantId, null, 5);
    allFieldIds.push(...standaloneFields.map(f => f.id));
  }

  // Create tasks
  console.log('📋 Creating tasks...');
  await createTasks(allFieldIds, TENANTS.DEMO);

  // Create NDVI readings
  console.log('📊 Creating NDVI readings...');
  await createNdviReadings(allFieldIds);

  // Create sync status entries
  console.log('📱 Creating sync status entries...');
  for (const tenantId of Object.values(TENANTS)) {
    for (let i = 0; i < 3; i++) {
      await prisma.syncStatus.create({
        data: {
          deviceId: `device-${tenantId.substring(0, 8)}-${i}`,
          userId: `user-${i}`,
          tenantId,
          lastSyncAt: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000),
          lastSyncVersion: BigInt(Math.floor(Math.random() * 1000)),
          status: 'idle',
          pendingUploads: Math.floor(Math.random() * 5),
          pendingDownloads: Math.floor(Math.random() * 10),
          deviceInfo: {
            platform: ['android', 'ios'][Math.floor(Math.random() * 2)],
            version: '1.0.0',
            model: ['Samsung Galaxy', 'iPhone 14', 'Pixel 7'][Math.floor(Math.random() * 3)],
          },
        },
      });
    }
  }

  // Summary
  const fieldCount = await prisma.field.count();
  const taskCount = await prisma.task.count();
  const ndviCount = await prisma.ndviReading.count();
  const syncCount = await prisma.syncStatus.count();

  console.log('\n✅ Seeding completed successfully!');
  console.log('✅ اكتمل البذر بنجاح!');
  console.log('─────────────────────────────────────');
  console.log(`📊 Summary / الملخص:`);
  console.log(`   - Farms / المزارع: ${farms.length}`);
  console.log(`   - Fields / الحقول: ${fieldCount}`);
  console.log(`   - Tasks / المهام: ${taskCount}`);
  console.log(`   - NDVI Readings / قراءات NDVI: ${ndviCount}`);
  console.log(`   - Sync Status / حالة المزامنة: ${syncCount}`);
  console.log('─────────────────────────────────────');
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
