/**
 * SAHOOL Field Management Service - Database Seeding
 * خدمة إدارة الحقول - بذر قاعدة البيانات
 *
 * Farms and fields are created through the application UI, not seeded here.
 * This script only seeds supporting data (sync status entries).
 *
 * Usage: npx prisma db seed
 */

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// Sample tenant IDs
// معرفات المستأجرين العينة
const TENANTS = {
  DEMO: 'tenant-demo-001',
  TEST: 'tenant-test-001',
  DEV: 'tenant-dev-001',
};

/**
 * Main seeding function
 * دالة البذر الرئيسية
 */
async function main() {
  console.log('🌱 Starting database seeding...');

  // Clear existing data
  console.log('🗑️ Clearing existing data...');
  await prisma.ndviReading.deleteMany();
  await prisma.task.deleteMany();
  await prisma.fieldBoundaryHistory.deleteMany();
  await prisma.field.deleteMany();
  await prisma.syncStatus.deleteMany();
  await prisma.$executeRaw`DELETE FROM farms`;

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
          pendingUploads: 0,
          pendingDownloads: 0,
          deviceInfo: {
            platform: ['android', 'ios'][Math.floor(Math.random() * 2)],
            version: '1.0.0',
            model: ['Samsung Galaxy', 'iPhone 14', 'Pixel 7'][Math.floor(Math.random() * 3)],
          },
        },
      });
    }
  }

  const syncCount = await prisma.syncStatus.count();

  console.log('\n✅ Seeding completed successfully!');
  console.log('─────────────────────────────────────');
  console.log(`   - Sync Status entries: ${syncCount}`);
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
