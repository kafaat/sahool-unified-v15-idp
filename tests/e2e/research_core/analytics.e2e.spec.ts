/**
 * E2E Tests - Analytics Module
 * اختبارات شاملة - وحدة التحليلات
 */
import { INestApplication, ValidationPipe } from '@nestjs/common';
import { Test, TestingModule } from '@nestjs/testing';
import * as request from 'supertest';
import { AppModule } from '@/app.module';
import { PrismaService } from '@/config/prisma.service';

describe('Analytics E2E (e2e)', () => {
  let app: INestApplication;
  let prisma: PrismaService;

  const testUserId = 'test-user-analytics';
  let testExperimentId: string;

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

    // Setup test data
    const experiment = await prisma.experiment.create({
      data: {
        title: 'Analytics Test Experiment',
        farmId: 'test-farm-analytics',
        principalResearcherId: testUserId,
        startDate: new Date('2025-01-01'),
        endDate: new Date('2025-12-31'),
        status: 'active',
      },
    });
    testExperimentId = experiment.id;

    // Create some test logs
    for (let i = 0; i < 10; i++) {
      await prisma.researchDailyLog.create({
        data: {
          experimentId: testExperimentId,
          logDate: new Date(`2025-01-${String(i + 1).padStart(2, '0')}`),
          category: i % 2 === 0 ? 'observation' : 'irrigation',
          title: `Test Log ${i + 1}`,
          notes: `Test notes for log ${i + 1}`,
          recordedBy: testUserId,
          hash: `test-hash-${i}`,
        },
      });
    }
  });

  afterAll(async () => {
    // Cleanup
    await prisma.researchDailyLog.deleteMany({
      where: { experimentId: testExperimentId },
    });
    await prisma.experiment.deleteMany({
      where: { id: testExperimentId },
    });
    await app.close();
  });

  describe('GET /analytics/dashboard', () => {
    it('should return dashboard overview', async () => {
      const response = await request(app.getHttpServer())
        .get('/analytics/dashboard')
        .expect(200);

      expect(response.body).toHaveProperty('summary');
      expect(response.body.summary).toHaveProperty('totalExperiments');
      expect(response.body.summary).toHaveProperty('totalLogs');
      expect(response.body).toHaveProperty('experimentsByStatus');
    });

    it('should filter dashboard by date range', async () => {
      const response = await request(app.getHttpServer())
        .get('/analytics/dashboard')
        .query({
          startDate: '2025-01-01',
          endDate: '2025-01-31',
        })
        .expect(200);

      expect(response.body).toHaveProperty('period');
      expect(response.body.period.startDate).toBe('2025-01-01');
    });

    it('should filter dashboard by experiment', async () => {
      const response = await request(app.getHttpServer())
        .get('/analytics/dashboard')
        .query({ experimentId: testExperimentId })
        .expect(200);

      expect(response.body.summary.totalLogs).toBeGreaterThan(0);
    });
  });

  describe('GET /analytics/kpis', () => {
    it('should calculate all KPIs', async () => {
      const response = await request(app.getHttpServer())
        .get('/analytics/kpis')
        .expect(200);

      expect(response.body).toHaveProperty('kpis');
      expect(response.body).toHaveProperty('calculatedAt');
      expect(response.body.kpis).toHaveProperty('experiment_progress');
      expect(response.body.kpis).toHaveProperty('log_completion');
    });

    it('should calculate specific KPIs', async () => {
      const response = await request(app.getHttpServer())
        .get('/analytics/kpis')
        .query({
          types: ['experiment_progress', 'data_integrity'],
        })
        .expect(200);

      expect(Object.keys(response.body.kpis)).toHaveLength(2);
    });

    it('should calculate KPIs for specific experiment', async () => {
      const response = await request(app.getHttpServer())
        .get('/analytics/kpis')
        .query({ experimentId: testExperimentId })
        .expect(200);

      expect(response.body.kpis.experiment_progress).toHaveProperty('value');
      expect(response.body.kpis.experiment_progress).toHaveProperty('status');
    });

    it('KPI should have correct structure', async () => {
      const response = await request(app.getHttpServer())
        .get('/analytics/kpis')
        .expect(200);

      const kpi = response.body.kpis.experiment_progress;
      expect(kpi).toHaveProperty('value');
      expect(kpi).toHaveProperty('target');
      expect(kpi).toHaveProperty('unit');
      expect(kpi).toHaveProperty('status');
      expect(typeof kpi.value).toBe('number');
    });
  });

  describe('GET /analytics/trends', () => {
    it('should return trend data', async () => {
      const response = await request(app.getHttpServer())
        .get('/analytics/trends')
        .query({
          metric: 'logs_count',
          experimentId: testExperimentId,
          dataPoints: 10,
        })
        .expect(200);

      expect(response.body).toHaveProperty('metric');
      expect(response.body).toHaveProperty('dataPoints');
      expect(response.body).toHaveProperty('trend');
      expect(Array.isArray(response.body.dataPoints)).toBe(true);
    });

    it('should calculate trend direction', async () => {
      const response = await request(app.getHttpServer())
        .get('/analytics/trends')
        .query({
          metric: 'logs_count',
          dataPoints: 5,
        })
        .expect(200);

      expect(['up', 'down', 'stable']).toContain(response.body.trend);
    });
  });

  describe('GET /analytics/experiments/:id', () => {
    it('should return experiment analytics', async () => {
      const response = await request(app.getHttpServer())
        .get(`/analytics/experiments/${testExperimentId}`)
        .expect(200);

      expect(response.body).toHaveProperty('experiment');
      expect(response.body).toHaveProperty('counts');
      expect(response.body).toHaveProperty('activity');
      expect(response.body.experiment.id).toBe(testExperimentId);
    });

    it('should include activity breakdown', async () => {
      const response = await request(app.getHttpServer())
        .get(`/analytics/experiments/${testExperimentId}`)
        .expect(200);

      expect(response.body.activity).toHaveProperty('logsByDate');
      expect(response.body.activity).toHaveProperty('logsByCategory');
      expect(Array.isArray(response.body.activity.logsByDate)).toBe(true);
    });

    it('should return null for non-existent experiment', async () => {
      const response = await request(app.getHttpServer())
        .get('/analytics/experiments/non-existent')
        .expect(200);

      expect(response.body).toBeNull();
    });
  });

  describe('GET /analytics/health', () => {
    it('should return system health', async () => {
      const response = await request(app.getHttpServer())
        .get('/analytics/health')
        .expect(200);

      expect(response.body).toHaveProperty('status');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('kpis');
      expect(response.body.status).toBe('healthy');
    });
  });
});
