/**
 * E2E Tests - Experiments Module
 * اختبارات شاملة - وحدة التجارب
 */
import { INestApplication, ValidationPipe } from '@nestjs/common';
import { Test, TestingModule } from '@nestjs/testing';
import * as request from 'supertest';
import { AppModule } from '@/app.module';
import { PrismaService } from '@/config/prisma.service';

describe('Experiments E2E (e2e)', () => {
  let app: INestApplication;
  let prisma: PrismaService;

  const testUserId = 'test-user-001';
  const testFarmId = 'test-farm-001';
  let createdExperimentId: string;

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
  });

  afterAll(async () => {
    // Cleanup test data
    if (createdExperimentId) {
      await prisma.experiment.deleteMany({
        where: { id: createdExperimentId },
      });
    }
    await app.close();
  });

  describe('POST /experiments', () => {
    it('should create a new experiment', async () => {
      const createDto = {
        title: 'E2E Test Experiment',
        titleAr: 'تجربة اختبار شاملة',
        description: 'Testing experiment creation',
        farmId: testFarmId,
        startDate: '2025-01-01',
        endDate: '2025-12-31',
        status: 'active',
        metadata: {
          cropType: 'wheat',
          season: 'winter',
        },
      };

      const response = await request(app.getHttpServer())
        .post('/experiments')
        .set('x-user-id', testUserId)
        .send(createDto)
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.title).toBe(createDto.title);
      expect(response.body.principalResearcherId).toBe(testUserId);

      createdExperimentId = response.body.id;
    });

    it('should reject invalid experiment data', async () => {
      const invalidDto = {
        // Missing required title
        description: 'Invalid experiment',
        farmId: testFarmId,
      };

      await request(app.getHttpServer())
        .post('/experiments')
        .set('x-user-id', testUserId)
        .send(invalidDto)
        .expect(400);
    });
  });

  describe('GET /experiments', () => {
    it('should return paginated experiments', async () => {
      const response = await request(app.getHttpServer())
        .get('/experiments')
        .query({ page: 1, limit: 10 })
        .expect(200);

      expect(response.body).toHaveProperty('data');
      expect(response.body).toHaveProperty('meta');
      expect(Array.isArray(response.body.data)).toBe(true);
      expect(response.body.meta).toHaveProperty('total');
      expect(response.body.meta).toHaveProperty('page');
    });

    it('should filter experiments by status', async () => {
      const response = await request(app.getHttpServer())
        .get('/experiments')
        .query({ status: 'active' })
        .expect(200);

      expect(response.body.data.every((e: any) => e.status === 'active')).toBe(
        true,
      );
    });

    it('should filter experiments by farmId', async () => {
      const response = await request(app.getHttpServer())
        .get('/experiments')
        .query({ farmId: testFarmId })
        .expect(200);

      expect(
        response.body.data.every((e: any) => e.farmId === testFarmId),
      ).toBe(true);
    });
  });

  describe('GET /experiments/:id', () => {
    it('should return experiment details', async () => {
      if (!createdExperimentId) {
        return;
      }

      const response = await request(app.getHttpServer())
        .get(`/experiments/${createdExperimentId}`)
        .expect(200);

      expect(response.body.id).toBe(createdExperimentId);
      expect(response.body).toHaveProperty('protocols');
      expect(response.body).toHaveProperty('plots');
    });

    it('should return 404 for non-existent experiment', async () => {
      await request(app.getHttpServer())
        .get('/experiments/non-existent-id')
        .expect(404);
    });
  });

  describe('PUT /experiments/:id', () => {
    it('should update experiment', async () => {
      if (!createdExperimentId) {
        return;
      }

      const updateDto = {
        title: 'Updated E2E Test Experiment',
        description: 'Updated description',
      };

      const response = await request(app.getHttpServer())
        .put(`/experiments/${createdExperimentId}`)
        .set('x-user-id', testUserId)
        .send(updateDto)
        .expect(200);

      expect(response.body.title).toBe(updateDto.title);
      expect(response.body.description).toBe(updateDto.description);
    });
  });

  describe('POST /experiments/:id/lock', () => {
    it('should lock experiment', async () => {
      if (!createdExperimentId) {
        return;
      }

      const response = await request(app.getHttpServer())
        .post(`/experiments/${createdExperimentId}/lock`)
        .set('x-user-id', testUserId)
        .expect(200);

      expect(response.body.status).toBe('locked');
      expect(response.body.lockedBy).toBe(testUserId);
    });

    it('should reject modifications on locked experiment', async () => {
      if (!createdExperimentId) {
        return;
      }

      await request(app.getHttpServer())
        .put(`/experiments/${createdExperimentId}`)
        .set('x-user-id', testUserId)
        .send({ title: 'Should fail' })
        .expect(403);
    });
  });

  describe('GET /experiments/:id/summary', () => {
    it('should return experiment summary with statistics', async () => {
      if (!createdExperimentId) {
        return;
      }

      const response = await request(app.getHttpServer())
        .get(`/experiments/${createdExperimentId}/summary`)
        .expect(200);

      expect(response.body).toHaveProperty('statistics');
      expect(response.body.statistics).toHaveProperty('logsCount');
      expect(response.body.statistics).toHaveProperty('samplesCount');
    });
  });

  describe('DELETE /experiments/:id', () => {
    it('should delete unlocked experiment', async () => {
      // Create a new experiment for deletion test
      const createResponse = await request(app.getHttpServer())
        .post('/experiments')
        .set('x-user-id', testUserId)
        .send({
          title: 'To Delete',
          farmId: testFarmId,
          startDate: '2025-01-01',
          status: 'draft',
        })
        .expect(201);

      const toDeleteId = createResponse.body.id;

      await request(app.getHttpServer())
        .delete(`/experiments/${toDeleteId}`)
        .set('x-user-id', testUserId)
        .expect(200);

      // Verify deletion
      await request(app.getHttpServer())
        .get(`/experiments/${toDeleteId}`)
        .expect(404);
    });
  });
});
