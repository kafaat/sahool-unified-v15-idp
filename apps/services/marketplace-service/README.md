# Marketplace Service - خدمة السوق

## نظرة عامة | Overview

خدمة السوق الزراعي لبيع وشراء المنتجات والمستلزمات الزراعية.

Agricultural marketplace service for buying and selling products and supplies.

**Port:** 3010
**Version:** 15.4.0

---

## الميزات | Features

### المنتجات | Products
| النوع | Type | الوصف |
|-------|------|--------|
| محاصيل | Crops | منتجات زراعية |
| مستلزمات | Supplies | بذور وأسمدة |
| معدات | Equipment | آلات ومعدات |
| خدمات | Services | خدمات زراعية |

### العمليات | Operations
| العملية | Operation | الوصف |
|---------|-----------|--------|
| بيع | Sell | عرض للبيع |
| شراء | Buy | طلب شراء |
| مزاد | Auction | مزاد علني |
| عقود | Contracts | عقود مستقبلية |

---

## API Endpoints

### المنتجات | Products

```http
# جلب المنتجات
GET /products?category=crops&region=sanaa&page=1&limit=20

# إضافة منتج
POST /products
{
    "title": "قمح يمني فاخر",
    "category": "crops",
    "subcategory": "wheat",
    "description": "قمح محلي عالي الجودة",
    "quantity": 5000,
    "unit": "kg",
    "price_sar_per_unit": 3.5,
    "location": {
        "region": "صنعاء",
        "district": "بني حشيش"
    },
    "images": ["https://..."],
    "harvest_date": "2024-01-10",
    "organic": false
}

# تفاصيل منتج
GET /products/{product_id}

# تحديث منتج
PATCH /products/{product_id}
{
    "price_sar_per_unit": 3.2,
    "quantity": 4500
}

# حذف منتج
DELETE /products/{product_id}
```

### الطلبات | Orders

```http
# إنشاء طلب
POST /orders
{
    "product_id": "prod-001",
    "quantity": 500,
    "delivery_address": {
        "region": "عدن",
        "address": "شارع المعلا"
    },
    "payment_method": "bank_transfer"
}

# جلب طلبات المشتري
GET /orders/buyer?status=pending

# جلب طلبات البائع
GET /orders/seller?status=pending

# تحديث حالة الطلب
PATCH /orders/{order_id}
{
    "status": "shipped",
    "tracking_number": "YE123456"
}

# إلغاء طلب
POST /orders/{order_id}/cancel
{
    "reason": "تأخر الشحن"
}
```

### التقييمات | Reviews

```http
# إضافة تقييم
POST /products/{product_id}/reviews
{
    "rating": 4,
    "comment": "منتج ممتاز وجودة عالية",
    "images": []
}

# جلب التقييمات
GET /products/{product_id}/reviews?page=1

# تقييم البائع
GET /sellers/{seller_id}/rating
```

### المزادات | Auctions

```http
# إنشاء مزاد
POST /auctions
{
    "product_id": "prod-001",
    "starting_price_sar": 10000,
    "min_increment_sar": 500,
    "start_time": "2024-01-20T10:00:00Z",
    "end_time": "2024-01-21T10:00:00Z"
}

# المزادات النشطة
GET /auctions?status=active

# تقديم مزايدة
POST /auctions/{auction_id}/bids
{
    "amount_sar": 11500
}

# تاريخ المزايدات
GET /auctions/{auction_id}/bids
```

### الأسعار | Prices

```http
# أسعار السوق
GET /prices?product=wheat&region=sanaa

Response:
{
    "product": "wheat",
    "region": "sanaa",
    "prices": {
        "current_avg_sar_kg": 3.2,
        "min_sar_kg": 2.8,
        "max_sar_kg": 3.8,
        "change_7d_percent": 5.2
    },
    "trend": "increasing",
    "volume_tons_7d": 250
}

# تاريخ الأسعار
GET /prices/history?product=wheat&period=30d
```

### البحث | Search

```http
# بحث متقدم
POST /search
{
    "query": "بذور طماطم",
    "filters": {
        "category": "supplies",
        "price_range": [10, 100],
        "region": "صنعاء"
    },
    "sort": "price_asc"
}
```

---

## نماذج البيانات | Data Models

### Product
```json
{
    "id": "prod-001",
    "seller_id": "user-001",
    "title": "قمح يمني فاخر",
    "title_en": "Premium Yemeni Wheat",
    "category": "crops",
    "subcategory": "wheat",
    "description": "قمح محلي عالي الجودة من مرتفعات صنعاء",
    "quantity": 5000,
    "unit": "kg",
    "price_sar_per_unit": 3.5,
    "total_price_sar": 17500,
    "location": {
        "region": "صنعاء",
        "coordinates": {"lat": 15.35, "lng": 44.15}
    },
    "images": ["https://..."],
    "status": "active",
    "views": 156,
    "created_at": "2024-01-15T10:00:00Z"
}
```

### Order
```json
{
    "id": "order-001",
    "product_id": "prod-001",
    "buyer_id": "user-002",
    "seller_id": "user-001",
    "quantity": 500,
    "unit_price_sar": 3.5,
    "total_price_sar": 1750,
    "status": "confirmed",
    "delivery": {
        "address": "عدن، شارع المعلا",
        "method": "shipping",
        "estimated_date": "2024-01-20"
    },
    "payment": {
        "method": "bank_transfer",
        "status": "paid"
    },
    "created_at": "2024-01-16T10:00:00Z"
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=3010
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...
REDIS_URL=redis://redis:6379

# التخزين
S3_BUCKET=sahool-marketplace

# الدفع
PAYMENT_GATEWAY_URL=...
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "marketplace-service",
    "version": "15.4.0"
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
