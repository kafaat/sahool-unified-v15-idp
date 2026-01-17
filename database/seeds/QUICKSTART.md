# SAHOOL Database Seeds - Quick Start Guide

## Installation

```bash
# Install dependencies
pip install psycopg2-binary

# Navigate to seeds directory
cd database/seeds
```

## Run All Seeds

```bash
# Using direct database URL
python seed_runner.py --db-url postgresql://user:password@localhost:5432/sahool

# Using environment variable
export DATABASE_URL="postgresql://user:password@localhost:5432/sahool"
python seed_runner.py

# Using environment name (development/staging/production)
export DATABASE_URL_DEV="postgresql://user:password@localhost:5432/sahool_dev"
python seed_runner.py --env development
```

## Docker Compose Example

If using docker-compose:

```bash
# Start database
docker-compose up -d postgres

# Run seeds
python seed_runner.py --db-url postgresql://sahool:sahool123@localhost:5432/sahool_db
```

## Verify Data

```bash
# Check what's in the database without running seeds
python seed_runner.py --db-url <your-url> --verify-only
```

## Default Users

After seeding, you can login with:

| Email                      | Password  | Role       | Region            |
| -------------------------- | --------- | ---------- | ----------------- |
| admin@sahool.ye            | admin123  | Admin      | System            |
| ahmed.alsanani@sahool.ye   | farmer123 | Farmer     | Sana'a            |
| mohammed.altaizi@sahool.ye | farmer123 | Farmer     | Ta'izz (Coffee)   |
| ali.alhadrami@sahool.ye    | farmer123 | Farmer     | Hadramout (Dates) |
| dr.khalid@sahool.ye        | admin123  | Agronomist | Advisory          |

⚠️ **IMPORTANT**: Change these passwords immediately in production!

## What Gets Created

- ✅ 10 users (admin, farmers, agronomists)
- ✅ 10 farms across Yemen governorates
- ✅ 30 fields with GeoJSON boundaries
- ✅ 50+ crops in catalog (cereals, vegetables, fruits, cash crops)
- ✅ 1 year of weather history for 5 cities
- ✅ 35+ inventory items + 6 suppliers
- ✅ 1,000+ satellite NDVI observations
- ✅ 30+ financial transactions + invoices

## Sample Queries

After seeding, try these queries:

```sql
-- View all farms by governorate
SELECT governorate, COUNT(*), SUM(total_area_hectares)
FROM farms
GROUP BY governorate;

-- View crop catalog by category
SELECT category, COUNT(*), AVG(price_yer_per_kg_avg)
FROM crop_catalog
GROUP BY category;

-- View recent NDVI observations
SELECT f.name, n.obs_date, n.ndvi_mean, n.cloud_coverage
FROM ndvi_observations n
JOIN fields f ON n.field_id = f.id
ORDER BY n.obs_date DESC
LIMIT 10;

-- View farmer transactions
SELECT u.name, t.transaction_type, t.category, t.amount, t.transaction_date
FROM transactions t
JOIN users u ON t.user_id = u.id
ORDER BY t.transaction_date DESC;

-- View inventory by category
SELECT category, COUNT(*), SUM(current_quantity * unit_cost) as total_value
FROM inventory_items
GROUP BY category;
```

## Troubleshooting

**Error: psycopg2 not installed**

```bash
pip install psycopg2-binary
```

**Error: connection refused**

- Check PostgreSQL is running
- Verify connection string (host, port, user, password, database)

**Error: table does not exist**

- Run database migrations first
- Or use the CREATE TABLE statements in the SQL files

**Error: duplicate key**

- Database already has data
- Uncomment TRUNCATE statements in SQL files to clear first

## Need Help?

See full documentation in `README.md`
