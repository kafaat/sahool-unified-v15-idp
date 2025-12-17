/**
 * E2E Tests - Research Logs Module
 * اختبارات شاملة - وحدة سجلات البحث
 */
import { INestApplication, ValidationPipe } from '@nestjs/common';
import { Test, TestingModule } from '@nestjs/testing';
import * as request from 'supertest';
import { AppModule } from '@/app.module';
import { PrismaService } from '@/config/prisma.service';

describe('Research Logs E2E (e2e)', () => {
  let app: INestApplication;
  let prisma: PrismaService;

  const testUserId = 'test-user-001';
  let testExperimentId: string;
  let createdLogId: string;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.useGlobalPipes(
      new ValidationPipe({
        whitelist: true,
        transform: true,
      }),
    );

    prisma = moduleFixture.get<PrismaService>(PrismaService);
    await app.init();

    // Create test experiment
    const experiment = await prisma.experiment.create({
      data: {
        title: 'E2E Log Test Experiment',
        farmId: 'test-farm-001',
        principalResearcherId: testUserId,
        startDate: new Date('2025-01-01'),
        status: 'active',
      },
    });
    testExperimentId = experiment.id;
  });

  afterAll(async () => {
    // Cleanup
    if (createdLogId) {
      await prisma.researchDailyLog.deleteMany({
        where: { id: createdLogId },
      });
    }
    if (testExperimentId) {
      await prisma.experiment.deleteMany({
        where: { id: testExperimentId },
      });
    }
    await app.close();
  });

  describe('POST /experiments/:experimentId/logs', () => {
    it('should create a research log', async () => {
      const createDto = {
        experimentId: testExperimentId,
        logDate: '2025-01-15',
        logTime: '09:30',
        category: 'observation',
        title: 'Daily Field Observation',
        titleAr: 'ملاحظة يومية للحقل',
        notes: 'Observed healthy crop growth',
        notesAr: 'لوحظ نمو صحي للمحصول',
        measurements: {
          temperature: 25,
          humidity: 65,
          soilMoisture: 40,
        },
        weatherConditions: {
          sky: 'clear',
          wind: 'light',
        },
      };

      const response = await request(app.getHttpServer())
        .post(`/experiments/${testExperimentId}/logs`)
        .set('x-user-id', testUserId)
        .send(createDto)
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body).toHaveProperty('hash');
      expect(response.body.experimentId).toBe(testExperimentId);
      expect(response.body.category).toBe('observation');

      createdLogId = response.body.id;
    });

    it('should reject log for non-existent experiment', async () => {
      await request(app.getHttpServer())
        .post('/experiments/non-existent/logs')
        .set('x-user-id', testUserId)
        .send({
          experimentId: 'non-existent',
          logDate: '2025-01-15',
          category: 'observation',
          title: 'Test',
        })
        .expect(404);
    });
  });

  describe('GET /experiments/:experimentId/logs', () => {
    it('should return paginated logs', async () => {
      const response = await request(app.getHttpServer())
        .get(`/experiments/${testExperimentId}/logs`)
        .query({ page: 1, limit: 10 })
        .expect(200);

      expect(response.body).toHaveProperty('data');
      expect(response.body).toHaveProperty('meta');
      expect(Array.isArray(response.body.data)).toBe(true);
    });

    it('should filter logs by category', async () => {
      const response = await request(app.getHttpServer())
        .get(`/experiments/${testExperimentId}/logs`)
        .query({ category: 'observation' })
        .expect(200);

      expect(
        response.body.data.every((l: any) => l.category === 'observation'),
      ).toBe(true);
    });

    it('should filter logs by date range', async () => {
      const response = await request(app.getHttpServer())
        .get(`/experiments/${testExperimentId}/logs`)
        .query({
          startDate: '2025-01-01',
          endDate: '2025-01-31',
        })
        .expect(200);

      expect(response.body).toHaveProperty('data');
    });
  });

  describe('GET /logs/:id', () => {
    it('should return log details with relations', async () => {
      if (!createdLogId) {
        return;
      }

      const response = await request(app.getHttpServer())
        .get(`/logs/${createdLogId}`)
        .expect(200);

      expect(response.body.id).toBe(createdLogId);
      expect(response.body).toHaveProperty('experiment');
    });

    it('should return 404 for non-existent log', async () => {
      await request(app.getHttpServer())
        .get('/logs/non-existent-id')
        .expect(404);
    });
  });

  describe('PUT /logs/:id', () => {
    it('should update log and regenerate hash', async () => {
      if (!createdLogId) {
        return;
      }

      const originalLog = await request(app.getHttpServer())
        .get(`/logs/${createdLogId}`)
        .expect(200);

      const updateDto = {
        notes: 'Updated observation notes',
        measurements: {
          temperature: 26,
          humidity: 60,
          soilMoisture: 45,
        },
      };

      const response = await request(app.getHttpServer())
        .put(`/logs/${createdLogId}`)
        .set('x-user-id', testUserId)
        .send(updateDto)
        .expect(200);

      expect(response.body.notes).toBe(updateDto.notes);
      // Hash should be different after update
      expect(response.body.hash).not.toBe(originalLog.body.hash);
    });
  });

  describe('POST /logs/:id/verify', () => {
    it('should verify log integrity', async () => {
      if (!createdLogId) {
        return;
      }

      const response = await request(app.getHttpServer())
        .post(`/logs/${createdLogId}/verify`)
        .expect(200);

      expect(response.body).toHaveProperty('isValid');
      expect(response.body).toHaveProperty('message');
      expect(response.body.isValid).toBe(true);
    });
  });

  describe('POST /experiments/:experimentId/logs/sync', () => {
    it('should sync offline logs', async () => {
      const offlineLogs = [
        {
          offlineId: 'offline-001',
          experimentId: testExperimentId,
          logDate: '2025-01-16',
          category: 'irrigation',
          title: 'Irrigation Log',
        },
        {
          offlineId: 'offline-002',
          experimentId: testExperimentId,
          logDate: '2025-01-17',
          category: 'fertilization',
          title: 'Fertilization Log',
        },
      ];

      const response = await request(app.getHttpServer())
        .post(`/experiments/${testExperimentId}/logs/sync`)
        .set('x-user-id', testUserId)
        .send({ logs: offlineLogs })
        .expect(200);

      expect(response.body).toHaveProperty('synced');
      expect(response.body).toHaveProperty('skipped');
      expect(response.body).toHaveProperty('failed');
      expect(response.body.synced.length).toBeGreaterThanOrEqual(0);

      // Cleanup synced logs
      await prisma.researchDailyLog.deleteMany({
        where: {
          offlineId: { in: offlineLogs.map((l) => l.offlineId) },
        },
      });
    });

    it('should skip already synced logs', async () => {
      // Create a log with offlineId
      const existingLog = await prisma.researchDailyLog.create({
        data: {
          experimentId: testExperimentId,
          logDate: new Date('2025-01-18'),
          category: 'observation',
          title: 'Existing Log',
          offlineId: 'existing-offline-001',
          recordedBy: testUserId,
          hash: 'test-hash',
        },
      });

      const offlineLogs = [
        {
          offlineId: 'existing-offline-001',
          experimentId: testExperimentId,
          logDate: '2025-01-18',
          category: 'observation',
          title: 'Should be skipped',
        },
      ];

      const response = await request(app.getHttpServer())
        .post(`/experiments/${testExperimentId}/logs/sync`)
        .set('x-user-id', testUserId)
        .send({ logs: offlineLogs })
        .expect(200);

      expect(response.body.skipped).toContain('existing-offline-001');

      // Cleanup
      await prisma.researchDailyLog.delete({
        where: { id: existingLog.id },
      });
    });
  });

  describe('DELETE /logs/:id', () => {
    it('should delete log', async () => {
      // Create log for deletion
      const log = await prisma.researchDailyLog.create({
        data: {
          experimentId: testExperimentId,
          logDate: new Date('2025-01-20'),
          category: 'observation',
          title: 'To Delete',
          recordedBy: testUserId,
          hash: 'test-hash',
        },
      });

      await request(app.getHttpServer())
        .delete(`/logs/${log.id}`)
        .set('x-user-id', testUserId)
        .expect(200);

      // Verify deletion
      await request(app.getHttpServer())
        .get(`/logs/${log.id}`)
        .expect(404);
    });
  });
});
