# Supply Chain Service | خدمة سلسلة التوريد

Connects farmers to agricultural suppliers for auto-purchasing based on advisory recommendations.

تربط المزارعين بموردي المستلزمات الزراعية للشراء التلقائي بناءً على التوصيات الاستشارية.

## Features | الميزات

- **Product Catalog** | كتالوج المنتجات: Browse agricultural supplies (seeds, fertilizers, pesticides, equipment)
- **Supplier Management** | إدارة الموردين: Find and compare suppliers by location, rating, and pricing
- **Order Management** | إدارة الطلبات: Create, track, and manage orders
- **Auto-Purchase** | الشراء التلقائي: Automatic purchasing from advisory recommendations
- **Delivery Tracking** | تتبع التوصيل: Real-time delivery tracking and notifications

## API Endpoints | نقاط الوصول

### Products | المنتجات

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products` | List products | قائمة المنتجات |
| GET | `/api/v1/products/{id}` | Get product details | تفاصيل المنتج |
| GET | `/api/v1/products/search` | Search products | البحث عن المنتجات |

### Suppliers | الموردين

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/suppliers` | List suppliers | قائمة الموردين |
| GET | `/api/v1/suppliers/{id}` | Get supplier details | تفاصيل المورد |
| GET | `/api/v1/suppliers/nearby` | Find nearby suppliers | الموردين القريبين |
| POST | `/api/v1/suppliers/{id}/quote` | Request quote | طلب عرض سعر |

### Orders | الطلبات

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/orders` | Create order | إنشاء طلب |
| GET | `/api/v1/orders` | List orders | قائمة الطلبات |
| GET | `/api/v1/orders/{id}` | Get order details | تفاصيل الطلب |
| POST | `/api/v1/orders/{id}/cancel` | Cancel order | إلغاء الطلب |
| GET | `/api/v1/orders/{id}/track` | Track delivery | تتبع التوصيل |

### Auto-Purchase | الشراء التلقائي

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auto-purchase` | Auto-purchase from recommendation | الشراء التلقائي |
| POST | `/api/v1/auto-purchase/compare` | Compare suppliers | مقارنة الموردين |
| POST | `/api/v1/auto-purchase/bulk` | Bulk purchase | شراء بالجملة |

### Health | الصحة

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Liveness probe | فحص الحياة |
| GET | `/readyz` | Readiness probe | فحص الجاهزية |
| GET | `/health` | Combined health check | فحص الصحة الشامل |

## Configuration | الإعدادات

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8230 | Service port |
| `DATABASE_URL` | - | PostgreSQL connection URL |
| `NATS_URL` | - | NATS connection URL |
| `REDIS_URL` | - | Redis connection URL |
| `PAYMENT_GATEWAY_URL` | - | Payment gateway URL |
| `DELIVERY_SERVICE_URL` | - | Delivery service URL |
| `NOTIFICATION_SERVICE_URL` | http://notification-service:8110 | Notification service URL |
| `AUTO_PURCHASE_ENABLED` | true | Enable auto-purchase feature |
| `SUPPLIER_SEARCH_RADIUS_KM` | 50 | Default supplier search radius |

## Development | التطوير

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m uvicorn src.main:app --reload --port 8230
```

### Running with Docker

```bash
# Build
docker build -t supply-chain-service .

# Run
docker run -p 8230:8230 supply-chain-service
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html
```

## Architecture | البنية

```
supply-chain-service/
├── src/
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   └── config.py        # Configuration settings
│   ├── api/
│   │   ├── schemas.py       # Pydantic models
│   │   └── endpoints/       # API routes
│   │       ├── products.py
│   │       ├── suppliers.py
│   │       ├── orders.py
│   │       └── auto_purchase.py
│   ├── suppliers/
│   │   ├── finder.py        # Supplier search logic
│   │   └── integrations.py  # Supplier API integrations
│   └── utils/
│       └── notifications.py # Notification utilities
├── tests/
│   ├── conftest.py
│   └── test_orders.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## Event Integration | التكامل مع الأحداث

The service publishes and subscribes to NATS events:

### Published Events | الأحداث المنشورة

- `sahool.{tenant}.order.created` - Order created
- `sahool.{tenant}.order.confirmed` - Order confirmed
- `sahool.{tenant}.order.shipped` - Order shipped
- `sahool.{tenant}.order.delivered` - Order delivered
- `sahool.{tenant}.order.cancelled` - Order cancelled

### Subscribed Events | الأحداث المشترك بها

- `sahool.{tenant}.advisory.recommendation` - New purchase recommendation
- `sahool.{tenant}.field.alert` - Field alert (may trigger purchase)

## License | الترخيص

Proprietary - KAFAAT
