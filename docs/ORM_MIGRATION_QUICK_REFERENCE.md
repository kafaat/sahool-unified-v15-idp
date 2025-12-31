# ORM Migration Quick Reference

## Summary

**Date**: 2025-12-31
**Status**: Ready for Implementation
**Estimated Time**: 3-5 days

---

## Current State

### ✅ Services Using Prisma (Standard - No Action Needed)

8 services already using Prisma 5.22.0:

1. `chat-service`
2. `crop-growth-model`
3. `disaster-assessment`
4. `lai-estimation`
5. `marketplace-service`
6. `research-core`
7. `yield-prediction`
8. `yield-prediction-service`

---

### ⚠️ Services Requiring Migration (HIGH PRIORITY)

2 services using TypeORM 0.3.20 that need migration:

| Service | Path | Priority | Complexity | Time |
|---------|------|----------|------------|------|
| **field-core** | `/apps/services/field-core` | HIGH | Medium | 2-3 days |
| **field-management-service** | `/apps/services/field-management-service` | HIGH | Medium | 1-2 days |

**Good News**: Both services already have complete Prisma schemas ready for migration!

---

## Migration Quick Start

### For field-core and field-management-service

```bash
# 1. Navigate to service
cd /home/user/sahool-unified-v15-idp/apps/services/field-core

# 2. Install dependencies
npm install

# 3. Set up environment
echo "DATABASE_URL=postgresql://sahool:sahool@postgres:5432/sahool" > .env

# 4. Generate Prisma Client
npm run prisma:generate

# 5. Create initial migration
npm run prisma:migrate:dev --name init_from_typeorm

# 6. Verify with Prisma Studio
npm run prisma:studio
```

---

## Key Migration Patterns

### Find One
```typescript
// Before (TypeORM)
const field = await fieldRepo.findOne({ where: { id } });

// After (Prisma)
const field = await prisma.field.findUnique({ where: { id } });
```

### Create
```typescript
// Before (TypeORM)
const newField = fieldRepo.create(data);
const saved = await fieldRepo.save(newField);

// After (Prisma)
const saved = await prisma.field.create({ data });
```

### Update
```typescript
// Before (TypeORM)
field.name = newName;
await fieldRepo.save(field);

// After (Prisma)
await prisma.field.update({
  where: { id },
  data: { name: newName }
});
```

### Raw SQL (PostGIS)
```typescript
// Before (TypeORM)
const fields = await AppDataSource.query(`SELECT ...`, [param]);

// After (Prisma)
const fields = await prisma.$queryRaw`SELECT ... WHERE id = ${param}`;
```

---

## Files to Update

### field-core

**Create**:
- `src/lib/prisma.ts` - Prisma client singleton

**Update**:
- `src/index.ts` - Replace all `AppDataSource.getRepository()` with `prisma.*`

**Remove**:
- `src/data-source.ts`
- `src/entity/Field.ts`
- `src/entity/FieldBoundaryHistory.ts`
- `src/entity/SyncStatus.ts`

**Update package.json**:
```json
{
  "dependencies": {
    "@prisma/client": "^5.22.0"
    // Remove: "typeorm", "reflect-metadata"
  },
  "devDependencies": {
    "prisma": "^5.22.0"
  }
}
```

---

## Testing Checklist

- [ ] All CRUD operations work
- [ ] PostGIS queries return correct results
- [ ] Transactions work correctly
- [ ] Optimistic locking (version field) works
- [ ] Mobile sync endpoints function properly
- [ ] Performance is acceptable

---

## Rollback Plan

If issues occur during migration:

```bash
# 1. Revert code changes
git checkout main -- src/

# 2. Reinstall dependencies
npm install

# 3. Database remains unchanged (TypeORM and Prisma can coexist temporarily)
```

---

## Support

- **Full Documentation**: `/docs/ORM_STANDARDIZATION.md`
- **Example Implementation**: `/apps/services/chat-service`
- **PostGIS Example**: Current service's `prisma/schema.prisma`

---

## Next Steps

1. Read full documentation: `/docs/ORM_STANDARDIZATION.md`
2. Schedule migration for `field-core` (2-3 days)
3. Apply learnings to `field-management-service` (1-2 days)
4. Update CI/CD pipelines
5. Monitor production after deployment

---

**For detailed migration guide, see**: `/docs/ORM_STANDARDIZATION.md`
