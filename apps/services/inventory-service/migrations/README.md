# Inventory Service Database Migrations

This directory contains Alembic database migrations for the Inventory Service.

## Migration Files

### Current Migrations

- **add_performance_indexes.py** (inv_0001_perf_indexes)
  - Adds performance-optimized indexes for common query patterns
  - Low stock item filtering
  - Expiry date tracking
  - Movement date range queries
  - SKU and barcode lookups
  - Transaction party references

## Running Migrations

### Upgrade to Latest Version
```bash
alembic upgrade head
```

### Downgrade One Version
```bash
alembic downgrade -1
```

### View Migration History
```bash
alembic history
```

### Generate New Migration
```bash
alembic revision -m "description of changes"
```

## Index Descriptions

### InventoryItem Indexes

1. **idx_inventory_items_low_stock**
   - Columns: `tenant_id, current_stock`
   - Condition: `WHERE current_stock <= reorder_level`
   - Purpose: Fast queries for low stock alerts and reorder suggestions

2. **idx_inventory_items_expiry**
   - Columns: `expiry_date`
   - Condition: `WHERE has_expiry = true AND expiry_date IS NOT NULL`
   - Purpose: Expiry tracking and FIFO/FEFO inventory management

3. **idx_inventory_items_sku_tenant**
   - Columns: `tenant_id, sku`
   - Purpose: Fast item lookups by SKU within tenant context

4. **idx_inventory_items_barcode**
   - Columns: `barcode`
   - Condition: `WHERE barcode IS NOT NULL`
   - Purpose: Barcode scanning operations

### InventoryMovement Indexes

1. **idx_inventory_movements_date_range**
   - Columns: `tenant_id, movement_date DESC`
   - Purpose: Efficient date range queries for movement history and audit trails

### InventoryTransaction Indexes

1. **idx_inventory_transactions_party**
   - Columns: `party_id`
   - Condition: `WHERE party_id IS NOT NULL`
   - Purpose: Customer/Supplier transaction history queries

## Notes

- All partial indexes use PostgreSQL-specific syntax
- Indexes are designed to support the most common query patterns
- Descending order on movement_date supports recent-first queries
- Partial indexes reduce index size and improve write performance
