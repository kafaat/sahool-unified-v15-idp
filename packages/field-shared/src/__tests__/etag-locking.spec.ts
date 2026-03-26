/**
 * ETag Locking Tests for SAHOOL Platform
 *
 * Tests validate optimistic locking with ETags for field operations.
 */

interface Field {
  id: string;
  name: string;
  areaHa: number;
  boundary: object | null;
  updatedAt: Date;
  etag: string;
}

interface ConflictResult {
  hasConflict: boolean;
  serverVersion?: Field;
  clientVersion?: Partial<Field>;
  resolution?: 'server_wins' | 'client_wins' | 'merge';
}

class ETagManager {
  private etags: Map<string, string> = new Map();

  generateETag(data: object): string {
    const str = JSON.stringify(data);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash;
    }
    return `"${Math.abs(hash).toString(16)}"`;
  }

  setETag(resourceId: string, etag: string): void {
    this.etags.set(resourceId, etag);
  }

  getETag(resourceId: string): string | undefined {
    return this.etags.get(resourceId);
  }

  validateETag(resourceId: string, clientETag: string): boolean {
    const serverETag = this.etags.get(resourceId);
    if (!serverETag) return true; // New resource
    return serverETag === clientETag;
  }

  clearETag(resourceId: string): void {
    this.etags.delete(resourceId);
  }
}

class FieldRepository {
  private fields: Map<string, Field> = new Map();
  private etagManager: ETagManager;

  constructor() {
    this.etagManager = new ETagManager();
  }

  create(field: Omit<Field, 'etag' | 'updatedAt'>): Field {
    const now = new Date();
    const fullField: Field = {
      ...field,
      updatedAt: now,
      etag: '',
    };

    fullField.etag = this.etagManager.generateETag(fullField);
    this.fields.set(field.id, fullField);
    this.etagManager.setETag(field.id, fullField.etag);

    return fullField;
  }

  get(id: string): Field | undefined {
    return this.fields.get(id);
  }

  update(
    id: string,
    updates: Partial<Field>,
    clientETag: string
  ): { success: boolean; field?: Field; conflict?: ConflictResult } {
    const existing = this.fields.get(id);
    if (!existing) {
      return { success: false };
    }

    // Validate ETag
    if (!this.etagManager.validateETag(id, clientETag)) {
      return {
        success: false,
        conflict: {
          hasConflict: true,
          serverVersion: existing,
          clientVersion: updates,
        },
      };
    }

    // Apply updates
    const updated: Field = {
      ...existing,
      ...updates,
      id: existing.id, // Prevent ID change
      updatedAt: new Date(),
      etag: '', // Will be regenerated
    };

    updated.etag = this.etagManager.generateETag(updated);
    this.fields.set(id, updated);
    this.etagManager.setETag(id, updated.etag);

    return { success: true, field: updated };
  }

  delete(id: string, clientETag: string): { success: boolean; conflict?: ConflictResult } {
    const existing = this.fields.get(id);
    if (!existing) {
      return { success: false };
    }

    if (!this.etagManager.validateETag(id, clientETag)) {
      return {
        success: false,
        conflict: {
          hasConflict: true,
          serverVersion: existing,
        },
      };
    }

    this.fields.delete(id);
    this.etagManager.clearETag(id);

    return { success: true };
  }

  getETag(id: string): string | undefined {
    return this.etagManager.getETag(id);
  }
}

class ConflictResolver {
  resolveServerWins(serverVersion: Field, _clientVersion: Partial<Field>): Field {
    return serverVersion;
  }

  resolveClientWins(serverVersion: Field, clientVersion: Partial<Field>): Field {
    return {
      ...serverVersion,
      ...clientVersion,
      id: serverVersion.id,
      updatedAt: new Date(),
      etag: '', // Will be regenerated
    };
  }

  resolveLastWriteWins(
    serverVersion: Field,
    clientVersion: Partial<Field>,
    clientTimestamp: Date
  ): Field {
    if (clientTimestamp > serverVersion.updatedAt) {
      return this.resolveClientWins(serverVersion, clientVersion);
    }
    return this.resolveServerWins(serverVersion, clientVersion);
  }

  resolveMerge(
    serverVersion: Field,
    clientVersion: Partial<Field>,
    conflictingFields: string[]
  ): { merged: Field; conflicts: string[] } {
    const merged: Field = { ...serverVersion };
    const unresolvedConflicts: string[] = [];

    for (const [key, value] of Object.entries(clientVersion)) {
      if (conflictingFields.includes(key)) {
        unresolvedConflicts.push(key);
      } else if (key !== 'id' && key !== 'etag' && key !== 'updatedAt') {
        (merged as Record<string, unknown>)[key] = value;
      }
    }

    merged.updatedAt = new Date();

    return { merged, conflicts: unresolvedConflicts };
  }
}

describe('ETagManager', () => {
  let etagManager: ETagManager;

  beforeEach(() => {
    etagManager = new ETagManager();
  });

  describe('ETag Generation', () => {
    it('should generate ETag from object', () => {
      const data = { id: '123', name: 'Test' };
      const etag = etagManager.generateETag(data);

      expect(etag).toBeDefined();
      expect(etag.startsWith('"')).toBe(true);
      expect(etag.endsWith('"')).toBe(true);
    });

    it('should generate different ETags for different data', () => {
      const etag1 = etagManager.generateETag({ name: 'Field A' });
      const etag2 = etagManager.generateETag({ name: 'Field B' });

      expect(etag1).not.toBe(etag2);
    });

    it('should generate same ETag for same data', () => {
      const data = { id: '123', name: 'Test' };
      const etag1 = etagManager.generateETag(data);
      const etag2 = etagManager.generateETag(data);

      expect(etag1).toBe(etag2);
    });
  });

  describe('ETag Storage', () => {
    it('should store and retrieve ETag', () => {
      etagManager.setETag('resource-1', '"abc123"');

      expect(etagManager.getETag('resource-1')).toBe('"abc123"');
    });

    it('should return undefined for unknown resource', () => {
      expect(etagManager.getETag('unknown')).toBeUndefined();
    });

    it('should clear ETag', () => {
      etagManager.setETag('resource-1', '"abc123"');
      etagManager.clearETag('resource-1');

      expect(etagManager.getETag('resource-1')).toBeUndefined();
    });
  });

  describe('ETag Validation', () => {
    it('should validate matching ETag', () => {
      etagManager.setETag('resource-1', '"abc123"');

      expect(etagManager.validateETag('resource-1', '"abc123"')).toBe(true);
    });

    it('should reject mismatched ETag', () => {
      etagManager.setETag('resource-1', '"abc123"');

      expect(etagManager.validateETag('resource-1', '"xyz789"')).toBe(false);
    });

    it('should allow new resource without ETag', () => {
      expect(etagManager.validateETag('new-resource', '"any"')).toBe(true);
    });
  });
});

describe('FieldRepository with ETag Locking', () => {
  let repo: FieldRepository;

  beforeEach(() => {
    repo = new FieldRepository();
  });

  describe('Create Operations', () => {
    it('should create field with ETag', () => {
      const field = repo.create({
        id: 'field-1',
        name: 'North Field',
        areaHa: 10.5,
        boundary: null,
      });

      expect(field.etag).toBeDefined();
      expect(field.updatedAt).toBeInstanceOf(Date);
    });

    it('should store ETag for created field', () => {
      const field = repo.create({
        id: 'field-1',
        name: 'North Field',
        areaHa: 10.5,
        boundary: null,
      });

      expect(repo.getETag('field-1')).toBe(field.etag);
    });
  });

  describe('Update Operations', () => {
    it('should update field with valid ETag', () => {
      const field = repo.create({
        id: 'field-1',
        name: 'North Field',
        areaHa: 10.5,
        boundary: null,
      });

      const result = repo.update('field-1', { name: 'Updated Field' }, field.etag);

      expect(result.success).toBe(true);
      expect(result.field?.name).toBe('Updated Field');
    });

    it('should reject update with stale ETag', () => {
      repo.create({
        id: 'field-1',
        name: 'North Field',
        areaHa: 10.5,
        boundary: null,
      });

      const result = repo.update('field-1', { name: 'Hacked' }, '"stale-etag"');

      expect(result.success).toBe(false);
      expect(result.conflict?.hasConflict).toBe(true);
    });

    it('should generate new ETag after update', () => {
      const field = repo.create({
        id: 'field-1',
        name: 'North Field',
        areaHa: 10.5,
        boundary: null,
      });

      const oldETag = field.etag;
      const result = repo.update('field-1', { name: 'Updated' }, field.etag);

      expect(result.field?.etag).not.toBe(oldETag);
    });

    it('should detect concurrent update conflict', () => {
      const field = repo.create({
        id: 'field-1',
        name: 'North Field',
        areaHa: 10.5,
        boundary: null,
      });

      // First update succeeds
      const result1 = repo.update('field-1', { name: 'Update 1' }, field.etag);
      expect(result1.success).toBe(true);

      // Second update with old ETag fails
      const result2 = repo.update('field-1', { name: 'Update 2' }, field.etag);
      expect(result2.success).toBe(false);
      expect(result2.conflict?.serverVersion?.name).toBe('Update 1');
    });
  });

  describe('Delete Operations', () => {
    it('should delete field with valid ETag', () => {
      const field = repo.create({
        id: 'field-1',
        name: 'North Field',
        areaHa: 10.5,
        boundary: null,
      });

      const result = repo.delete('field-1', field.etag);

      expect(result.success).toBe(true);
      expect(repo.get('field-1')).toBeUndefined();
    });

    it('should reject delete with stale ETag', () => {
      repo.create({
        id: 'field-1',
        name: 'North Field',
        areaHa: 10.5,
        boundary: null,
      });

      const result = repo.delete('field-1', '"stale-etag"');

      expect(result.success).toBe(false);
      expect(result.conflict?.hasConflict).toBe(true);
    });
  });
});

describe('ConflictResolver', () => {
  let resolver: ConflictResolver;
  let serverVersion: Field;
  let clientVersion: Partial<Field>;

  beforeEach(() => {
    resolver = new ConflictResolver();
    serverVersion = {
      id: 'field-1',
      name: 'Server Name',
      areaHa: 10,
      boundary: null,
      updatedAt: new Date('2024-01-15T10:00:00Z'),
      etag: '"server-etag"',
    };
    clientVersion = {
      name: 'Client Name',
      areaHa: 15,
    };
  });

  describe('Server Wins Strategy', () => {
    it('should return server version', () => {
      const result = resolver.resolveServerWins(serverVersion, clientVersion);

      expect(result.name).toBe('Server Name');
      expect(result.areaHa).toBe(10);
    });
  });

  describe('Client Wins Strategy', () => {
    it('should apply client changes', () => {
      const result = resolver.resolveClientWins(serverVersion, clientVersion);

      expect(result.name).toBe('Client Name');
      expect(result.areaHa).toBe(15);
    });

    it('should preserve server ID', () => {
      const result = resolver.resolveClientWins(serverVersion, { ...clientVersion, id: 'hacked' });

      expect(result.id).toBe('field-1');
    });
  });

  describe('Last Write Wins Strategy', () => {
    it('should use client version when client is newer', () => {
      const clientTimestamp = new Date('2024-01-15T11:00:00Z');
      const result = resolver.resolveLastWriteWins(serverVersion, clientVersion, clientTimestamp);

      expect(result.name).toBe('Client Name');
    });

    it('should use server version when server is newer', () => {
      const clientTimestamp = new Date('2024-01-15T09:00:00Z');
      const result = resolver.resolveLastWriteWins(serverVersion, clientVersion, clientTimestamp);

      expect(result.name).toBe('Server Name');
    });
  });

  describe('Merge Strategy', () => {
    it('should merge non-conflicting fields', () => {
      const { merged, conflicts } = resolver.resolveMerge(serverVersion, { areaHa: 20 }, ['name']);

      expect(merged.areaHa).toBe(20);
      expect(merged.name).toBe('Server Name');
      expect(conflicts).toHaveLength(0);
    });

    it('should report conflicting fields', () => {
      const { merged, conflicts } = resolver.resolveMerge(
        serverVersion,
        { name: 'Client Name', areaHa: 20 },
        ['name']
      );

      expect(conflicts).toContain('name');
      expect(merged.name).toBe('Server Name');
      expect(merged.areaHa).toBe(20);
    });
  });
});
