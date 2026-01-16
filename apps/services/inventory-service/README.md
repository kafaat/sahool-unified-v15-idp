# SAHOOL Inventory Service

Agricultural inventory management with advanced analytics and forecasting.

## Features

### Core Functionality

- **Inventory Management**: Multi-tenant inventory tracking with categories, warehouses, and suppliers
- **Stock Movements**: Receipt, issue, transfer, adjustment, return, write-off tracking
- **Transaction Recording**: Purchase, sale, use, waste, and return transactions

### Analytics & Forecasting

- **Consumption Forecasting**: Moving average-based forecasting with seasonal adjustment
- **Inventory Valuation**: FIFO and weighted average cost valuation
- **ABC/Pareto Analysis**: Classify items by value contribution
- **Turnover Analysis**: Calculate inventory turnover ratios and days of inventory
- **Slow-Moving & Dead Stock**: Identify items with low turnover or near expiry
- **Seasonal Patterns**: Analyze seasonal consumption trends
- **Cost Analysis**: Track input costs by field, crop, and category
- **Waste Analysis**: Monitor write-offs, expired items, and losses
- **Reorder Recommendations**: Smart reorder suggestions based on consumption and lead times

## API Endpoints

See full endpoint documentation in the service.

## Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/sahool_inventory
PORT=8115
SQL_ECHO=false
```

## Port

Default: **8115**
