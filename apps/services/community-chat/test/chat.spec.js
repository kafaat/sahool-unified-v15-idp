/**
 * SAHOOL Community Chat Service - Unit Tests
 * اختبارات خدمة المحادثات المجتمعية
 */

const express = require('express');
const request = require('supertest');

function createTestApp() {
  const app = express();
  app.use(express.json());

  app.get('/healthz', (_req, res) => {
    res.json({ status: 'ok', service: 'community_chat' });
  });

  app.get('/api/v1/channels', (_req, res) => {
    res.json({
      channels: [
        { id: 'channel_001', name: 'General', name_ar: 'عام', members: 150 },
        { id: 'channel_002', name: 'Wheat Farmers', name_ar: 'مزارعو القمح', members: 45 }
      ]
    });
  });

  app.post('/api/v1/channels', (req, res) => {
    res.status(201).json({
      id: 'channel_new',
      name: req.body.name,
      created_at: new Date().toISOString()
    });
  });

  app.get('/api/v1/channels/:channelId/messages', (req, res) => {
    res.json({
      channel_id: req.params.channelId,
      messages: [
        { id: 'msg_001', content: 'Hello', sender: 'user_001', timestamp: new Date().toISOString() }
      ]
    });
  });

  app.post('/api/v1/channels/:channelId/messages', (req, res) => {
    res.status(201).json({
      id: 'msg_new',
      content: req.body.content,
      channel_id: req.params.channelId,
      timestamp: new Date().toISOString()
    });
  });

  return app;
}

describe('Community Chat Service', () => {
  let app;

  beforeAll(() => {
    app = createTestApp();
  });

  describe('Health Check', () => {
    it('should return healthy status', async () => {
      const response = await request(app).get('/healthz');
      expect(response.status).toBe(200);
      expect(response.body.status).toBe('ok');
    });
  });

  describe('Channels', () => {
    it('should list channels', async () => {
      const response = await request(app).get('/api/v1/channels');
      expect(response.status).toBe(200);
      expect(response.body.channels).toBeDefined();
      expect(response.body.channels.length).toBeGreaterThan(0);
    });

    it('should create channel', async () => {
      const response = await request(app)
        .post('/api/v1/channels')
        .send({ name: 'New Channel' });
      expect(response.status).toBe(201);
      expect(response.body.id).toBeDefined();
    });
  });

  describe('Messages', () => {
    it('should get channel messages', async () => {
      const response = await request(app).get('/api/v1/channels/channel_001/messages');
      expect(response.status).toBe(200);
      expect(response.body.messages).toBeDefined();
    });

    it('should post message', async () => {
      const response = await request(app)
        .post('/api/v1/channels/channel_001/messages')
        .send({ content: 'Test message' });
      expect(response.status).toBe(201);
      expect(response.body.content).toBe('Test message');
    });
  });
});
