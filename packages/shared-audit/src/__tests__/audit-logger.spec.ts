/**
 * Audit Logger Tests for SAHOOL Platform
 *
 * Tests validate audit logging, hash chain integrity, and change tracking.
 */

interface AuditEntry {
  id: string;
  timestamp: Date;
  tenantId: string;
  userId: string;
  action: string;
  resourceType: string;
  resourceId: string;
  changes?: Record<string, { old: unknown; new: unknown }>;
  metadata?: Record<string, unknown>;
  hash: string;
  previousHash: string;
}

interface AuditLoggerConfig {
  hashAlgorithm: 'sha256' | 'sha384' | 'sha512';
  includeChanges: boolean;
  redactSensitiveFields: boolean;
  sensitiveFields: string[];
}

// Simple hash function for testing
function simpleHash(data: string): string {
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    const char = data.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16).padStart(16, '0');
}

class AuditLogger {
  private entries: AuditEntry[] = [];
  private config: AuditLoggerConfig;

  constructor(config: Partial<AuditLoggerConfig> = {}) {
    this.config = {
      hashAlgorithm: config.hashAlgorithm || 'sha256',
      includeChanges: config.includeChanges ?? true,
      redactSensitiveFields: config.redactSensitiveFields ?? true,
      sensitiveFields: config.sensitiveFields || ['password', 'token', 'secret', 'apiKey'],
    };
  }

  log(entry: Omit<AuditEntry, 'id' | 'timestamp' | 'hash' | 'previousHash'>): AuditEntry {
    const previousHash =
      this.entries.length > 0 ? this.entries[this.entries.length - 1].hash : '0'.repeat(16);

    const timestamp = new Date();
    const id = `audit-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Redact sensitive fields if enabled
    let changes = entry.changes;
    if (this.config.redactSensitiveFields && changes) {
      changes = this.redactChanges(changes);
    }

    const dataToHash = JSON.stringify({
      id,
      timestamp: timestamp.toISOString(),
      ...entry,
      changes,
      previousHash,
    });

    const hash = simpleHash(dataToHash);

    const auditEntry: AuditEntry = {
      id,
      timestamp,
      ...entry,
      changes,
      hash,
      previousHash,
    };

    this.entries.push(auditEntry);
    return auditEntry;
  }

  private redactChanges(
    changes: Record<string, { old: unknown; new: unknown }>
  ): Record<string, { old: unknown; new: unknown }> {
    const redacted: Record<string, { old: unknown; new: unknown }> = {};

    for (const [key, value] of Object.entries(changes)) {
      if (this.config.sensitiveFields.some((f) => key.toLowerCase().includes(f.toLowerCase()))) {
        redacted[key] = { old: '[REDACTED]', new: '[REDACTED]' };
      } else {
        redacted[key] = value;
      }
    }

    return redacted;
  }

  getEntries(): AuditEntry[] {
    return [...this.entries];
  }

  getEntriesByTenant(tenantId: string): AuditEntry[] {
    return this.entries.filter((e) => e.tenantId === tenantId);
  }

  getEntriesByUser(userId: string): AuditEntry[] {
    return this.entries.filter((e) => e.userId === userId);
  }

  getEntriesByResource(resourceType: string, resourceId: string): AuditEntry[] {
    return this.entries.filter(
      (e) => e.resourceType === resourceType && e.resourceId === resourceId
    );
  }

  verifyChain(): { valid: boolean; brokenAt?: number } {
    for (let i = 1; i < this.entries.length; i++) {
      if (this.entries[i].previousHash !== this.entries[i - 1].hash) {
        return { valid: false, brokenAt: i };
      }
    }
    return { valid: true };
  }

  verifyEntry(index: number): boolean {
    const entry = this.entries[index];
    if (!entry) return false;

    const previousHash = index > 0 ? this.entries[index - 1].hash : '0'.repeat(16);
    return entry.previousHash === previousHash;
  }
}

describe('AuditLogger', () => {
  let logger: AuditLogger;

  beforeEach(() => {
    logger = new AuditLogger();
  });

  describe('Basic Logging', () => {
    it('should create audit entry with required fields', () => {
      const entry = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'field.create',
        resourceType: 'field',
        resourceId: 'field-789',
      });

      expect(entry.id).toBeDefined();
      expect(entry.timestamp).toBeInstanceOf(Date);
      expect(entry.tenantId).toBe('tenant-123');
      expect(entry.userId).toBe('user-456');
      expect(entry.action).toBe('field.create');
      expect(entry.hash).toBeDefined();
    });

    it('should include changes when provided', () => {
      const entry = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'field.update',
        resourceType: 'field',
        resourceId: 'field-789',
        changes: {
          name: { old: 'Old Field', new: 'New Field' },
          area_ha: { old: 10, new: 15 },
        },
      });

      expect(entry.changes).toBeDefined();
      expect(entry.changes!.name.old).toBe('Old Field');
      expect(entry.changes!.name.new).toBe('New Field');
    });

    it('should include metadata when provided', () => {
      const entry = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'field.view',
        resourceType: 'field',
        resourceId: 'field-789',
        metadata: {
          ipAddress: '192.168.1.1',
          userAgent: 'Mozilla/5.0',
        },
      });

      expect(entry.metadata).toBeDefined();
      expect(entry.metadata!.ipAddress).toBe('192.168.1.1');
    });
  });

  describe('Hash Chain Integrity', () => {
    it('should create hash chain across entries', () => {
      const entry1 = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'field.create',
        resourceType: 'field',
        resourceId: 'field-1',
      });

      const entry2 = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'field.update',
        resourceType: 'field',
        resourceId: 'field-1',
      });

      expect(entry2.previousHash).toBe(entry1.hash);
    });

    it('should verify valid chain', () => {
      logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'action1',
        resourceType: 'resource',
        resourceId: 'id1',
      });

      logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'action2',
        resourceType: 'resource',
        resourceId: 'id2',
      });

      logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'action3',
        resourceType: 'resource',
        resourceId: 'id3',
      });

      const result = logger.verifyChain();
      expect(result.valid).toBe(true);
    });

    it('should have first entry with zero previous hash', () => {
      const entry = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'first.action',
        resourceType: 'resource',
        resourceId: 'id1',
      });

      expect(entry.previousHash).toBe('0000000000000000');
    });

    it('should verify individual entry', () => {
      logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'action1',
        resourceType: 'resource',
        resourceId: 'id1',
      });

      logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'action2',
        resourceType: 'resource',
        resourceId: 'id2',
      });

      expect(logger.verifyEntry(0)).toBe(true);
      expect(logger.verifyEntry(1)).toBe(true);
    });
  });

  describe('Sensitive Data Redaction', () => {
    it('should redact password fields', () => {
      const entry = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'user.update',
        resourceType: 'user',
        resourceId: 'user-789',
        changes: {
          password: { old: 'oldSecret123', new: 'newSecret456' },
          name: { old: 'John', new: 'Jane' },
        },
      });

      expect(entry.changes!.password.old).toBe('[REDACTED]');
      expect(entry.changes!.password.new).toBe('[REDACTED]');
      expect(entry.changes!.name.old).toBe('John');
    });

    it('should redact token fields', () => {
      const entry = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'api.update',
        resourceType: 'api',
        resourceId: 'api-123',
        changes: {
          apiToken: { old: 'token123', new: 'token456' },
        },
      });

      expect(entry.changes!.apiToken.old).toBe('[REDACTED]');
    });

    it('should not redact non-sensitive fields', () => {
      const entry = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'field.update',
        resourceType: 'field',
        resourceId: 'field-789',
        changes: {
          name: { old: 'Field A', new: 'Field B' },
          area_ha: { old: 10, new: 20 },
        },
      });

      expect(entry.changes!.name.old).toBe('Field A');
      expect(entry.changes!.area_ha.old).toBe(10);
    });

    it('should allow disabling redaction', () => {
      const noRedactLogger = new AuditLogger({ redactSensitiveFields: false });

      const entry = noRedactLogger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'user.update',
        resourceType: 'user',
        resourceId: 'user-789',
        changes: {
          password: { old: 'oldSecret', new: 'newSecret' },
        },
      });

      expect(entry.changes!.password.old).toBe('oldSecret');
    });
  });

  describe('Query Methods', () => {
    beforeEach(() => {
      logger.log({
        tenantId: 'tenant-A',
        userId: 'user-1',
        action: 'field.create',
        resourceType: 'field',
        resourceId: 'field-1',
      });

      logger.log({
        tenantId: 'tenant-A',
        userId: 'user-2',
        action: 'field.update',
        resourceType: 'field',
        resourceId: 'field-1',
      });

      logger.log({
        tenantId: 'tenant-B',
        userId: 'user-1',
        action: 'field.create',
        resourceType: 'field',
        resourceId: 'field-2',
      });
    });

    it('should get all entries', () => {
      const entries = logger.getEntries();
      expect(entries).toHaveLength(3);
    });

    it('should filter by tenant', () => {
      const entries = logger.getEntriesByTenant('tenant-A');
      expect(entries).toHaveLength(2);
      expect(entries.every((e) => e.tenantId === 'tenant-A')).toBe(true);
    });

    it('should filter by user', () => {
      const entries = logger.getEntriesByUser('user-1');
      expect(entries).toHaveLength(2);
      expect(entries.every((e) => e.userId === 'user-1')).toBe(true);
    });

    it('should filter by resource', () => {
      const entries = logger.getEntriesByResource('field', 'field-1');
      expect(entries).toHaveLength(2);
      expect(entries.every((e) => e.resourceId === 'field-1')).toBe(true);
    });
  });

  describe('Action Types', () => {
    it('should log create actions', () => {
      const entry = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'field.create',
        resourceType: 'field',
        resourceId: 'field-789',
      });

      expect(entry.action).toBe('field.create');
    });

    it('should log update actions', () => {
      const entry = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'field.update',
        resourceType: 'field',
        resourceId: 'field-789',
        changes: {
          name: { old: 'A', new: 'B' },
        },
      });

      expect(entry.action).toBe('field.update');
      expect(entry.changes).toBeDefined();
    });

    it('should log delete actions', () => {
      const entry = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'field.delete',
        resourceType: 'field',
        resourceId: 'field-789',
      });

      expect(entry.action).toBe('field.delete');
    });

    it('should log view/read actions', () => {
      const entry = logger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'field.view',
        resourceType: 'field',
        resourceId: 'field-789',
      });

      expect(entry.action).toBe('field.view');
    });
  });

  describe('Configuration', () => {
    it('should use default configuration', () => {
      const defaultLogger = new AuditLogger();
      const entry = defaultLogger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'test',
        resourceType: 'test',
        resourceId: 'test-1',
      });

      expect(entry.hash).toBeDefined();
    });

    it('should allow custom sensitive fields', () => {
      const customLogger = new AuditLogger({
        sensitiveFields: ['customSecret', 'privateKey'],
      });

      const entry = customLogger.log({
        tenantId: 'tenant-123',
        userId: 'user-456',
        action: 'test',
        resourceType: 'test',
        resourceId: 'test-1',
        changes: {
          customSecret: { old: 'secret1', new: 'secret2' },
          normalField: { old: 'value1', new: 'value2' },
        },
      });

      expect(entry.changes!.customSecret.old).toBe('[REDACTED]');
      expect(entry.changes!.normalField.old).toBe('value1');
    });
  });
});
