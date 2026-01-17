#!/usr/bin/env node
/**
 * Cross-platform Prisma Generate Script
 * سكربت توليد Prisma متوافق مع جميع الأنظمة
 *
 * Works on Windows, Linux, and macOS
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const servicesDir = path.join(__dirname, '..', 'apps', 'services');

// Check if services directory exists
if (!fs.existsSync(servicesDir)) {
  console.log('ℹ️  No services directory found, skipping prisma generate');
  process.exit(0);
}

// Find all service directories with prisma folder
const services = fs.readdirSync(servicesDir).filter(service => {
  const prismaDir = path.join(servicesDir, service, 'prisma');
  return fs.existsSync(prismaDir) && fs.statSync(prismaDir).isDirectory();
});

if (services.length === 0) {
  console.log('ℹ️  No Prisma schemas found, skipping');
  process.exit(0);
}

console.log(`🔄 Generating Prisma clients for ${services.length} service(s)...`);

let successCount = 0;
let failCount = 0;

for (const service of services) {
  const serviceDir = path.join(servicesDir, service);
  try {
    execSync('npx prisma generate', {
      cwd: serviceDir,
      stdio: 'pipe', // Suppress output
      timeout: 60000, // 60 second timeout
    });
    successCount++;
  } catch (error) {
    // Silently continue on error (same behavior as original script)
    failCount++;
  }
}

if (successCount > 0) {
  console.log(`✅ Prisma generate completed: ${successCount} success, ${failCount} skipped`);
}

process.exit(0);
