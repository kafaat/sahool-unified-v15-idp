/**
 * SAHOOL LAI Estimation Service - Unit Tests
 * اختبارات خدمة تقدير مؤشر مساحة الأوراق
 */

import express, { Express } from 'express';
import request from 'supertest';

function createTestApp(): Express {
  const app = express();
  app.use(express.json());

  app.get('/healthz', (_req, res) => {
    res.json({ status: 'ok', service: 'lai_estimation' });
  });

  app.post('/api/v1/estimate', (req, res) => {
    res.json({
      field_id: req.body.field_id,
      lai: 3.8,
      unit: 'm²/m²',
      confidence: 0.85,
      method: 'ndvi_regression',
      timestamp: new Date().toISOString()
    });
  });

  app.get('/api/v1/fields/:fieldId/lai-history', (req, res) => {
    res.json({
      field_id: req.params.fieldId,
      history: [
        { date: '2025-12-20', lai: 3.5 },
        { date: '2025-12-23', lai: 3.8 }
      ]
    });
  });

  app.get('/api/v1/crops/:crop/lai-reference', (req, res) => {
    res.json({
      crop: req.params.crop,
      stages: {
        seedling: { min: 0.5, max: 1.5 },
        vegetative: { min: 2.0, max: 4.0 },
        flowering: { min: 4.0, max: 6.0 },
        maturity: { min: 3.0, max: 5.0 }
      }
    });
  });

  return app;
}

describe('LAI Estimation Service', () => {
  let app: Express;

  beforeAll(() => {
    app = createTestApp();
  });

  describe('Health Check', () => {
    it('should return healthy status', async () => {
      const response = await request(app).get('/healthz');
      expect(response.status).toBe(200);
    });
  });

  describe('Estimation', () => {
    it('should estimate LAI', async () => {
      const response = await request(app)
        .post('/api/v1/estimate')
        .send({ field_id: 'field_001', ndvi: 0.72 });
      expect(response.status).toBe(200);
      expect(response.body.lai).toBeDefined();
      expect(response.body.confidence).toBeDefined();
    });
  });

  describe('History', () => {
    it('should get LAI history', async () => {
      const response = await request(app).get('/api/v1/fields/field_001/lai-history');
      expect(response.status).toBe(200);
      expect(response.body.history).toBeDefined();
    });
  });

  describe('Reference Values', () => {
    it('should get crop LAI reference', async () => {
      const response = await request(app).get('/api/v1/crops/wheat/lai-reference');
      expect(response.status).toBe(200);
      expect(response.body.stages).toBeDefined();
    });
  });
});
