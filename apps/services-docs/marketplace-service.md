# Marketplace Service Documentation

> **Service**: marketplace-service
> **Version**: 16.0.0
> **Type**: Node.js / NestJS
> **Port**: 3010
> **API Base**: `/api/v1`

## Overview

The Marketplace Service is a comprehensive agricultural marketplace and fintech platform for the SAHOOL ecosystem. It provides B2B/B2C trading capabilities, digital wallet management, Islamic finance-compatible agricultural loans, and credit scoring based on farm data.

### Key Features

- **Agricultural Marketplace**: Products (harvests, seeds, fertilizers, equipment)
- **Digital Wallet**: Balance management with double-spend protection
- **Credit Scoring**: Multi-factor scoring based on farm data
- **Agricultural Loans**: Islamic finance compatible (0% interest, admin fees only)
- **Escrow System**: Transaction protection for marketplace orders
- **Seller/Buyer Profiles**: Business profiles with ratings and statistics
- **Product Reviews**: Rating system with seller responses

---

## Kong Gateway Routes

| Route | Host | Port | Strip Path |
|-------|------|------|------------|
| `/api/v1/marketplace` | marketplace-service | 3010 | true |
| `/marketplace` | marketplace-service | 3010 | true |

---

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@postgres:5432/sahool` |
| `JWT_SECRET_KEY` | JWT signing secret (32+ chars) | `your-secret-key-32-characters-min` |
| `PORT` | Service port | `3010` |
| `NODE_ENV` | Environment | `production` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `NATS_URL` | NATS connection string | `nats://localhost:4222` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated CORS origins | `https://sahool.com,https://app.sahool.com` |
| `DATABASE_URL_DIRECT` | Direct DB URL (bypasses PgBouncer) | - |

### Missing/Recommended Environment Variables

The following environment variables are NOT currently used but SHOULD be added for production:

1. **`LOG_LEVEL`** - For configurable logging levels (currently hardcoded)
2. **`RATE_LIMIT_TTL`** - For configurable rate limiting
3. **`RATE_LIMIT_LIMIT`** - For configurable rate limits
4. **`ESCROW_FEE_PERCENTAGE`** - Fee for escrow transactions (hardcoded as 0)
5. **`SERVICE_FEE_PERCENTAGE`** - Order service fee (hardcoded as 2%)
6. **`DELIVERY_FEE`** - Delivery fee amount (hardcoded as 500 YER)
7. **`LOAN_ADMIN_FEE_PERCENTAGE`** - Loan admin fee (hardcoded as 2%)

---

## Database Schema

### Core Models

| Model | Description |
|-------|-------------|
| `Product` | Marketplace products (harvests, seeds, equipment) |
| `Order` | Purchase orders with items |
| `OrderItem` | Individual items in an order |
| `Wallet` | User digital wallet with credit scoring |
| `Transaction` | Financial transactions |
| `Loan` | Agricultural loans |
| `CreditEvent` | Credit history events |
| `Escrow` | Transaction protection |
| `ScheduledPayment` | Recurring payments |
| `WalletAuditLog` | Financial audit trail |
| `SellerProfile` | Seller business profiles |
| `BuyerProfile` | Buyer profiles with shipping addresses |
| `ProductReview` | Product ratings and reviews |
| `ReviewResponse` | Seller responses to reviews |

### Key Enums

```typescript
// Product Categories
ProductCategory: HARVEST | SEEDS | FERTILIZER | PESTICIDE | EQUIPMENT | IRRIGATION | OTHER

// Seller Types
SellerType: FARMER | COMPANY | COOPERATIVE

// Order Status
OrderStatus: PENDING | CONFIRMED | PROCESSING | SHIPPED | DELIVERED | CANCELLED

// Payment Status
PaymentStatus: UNPAID | PARTIAL | PAID | REFUNDED

// Credit Tiers
CreditTier: BRONZE (300-499) | SILVER (500-649) | GOLD (650-749) | PLATINUM (750-850)

// Loan Status
LoanStatus: PENDING | APPROVED | ACTIVE | PAID | DEFAULTED | REJECTED

// Loan Purpose
LoanPurpose: SEEDS | FERTILIZER | EQUIPMENT | IRRIGATION | EXPANSION | EMERGENCY | OTHER

// Escrow Status
EscrowStatus: HELD | RELEASED | REFUNDED | DISPUTED | CANCELLED

// Business Type
BusinessType: INDIVIDUAL | FARM | COOPERATIVE | DISTRIBUTOR | RETAILER
```

---

## API Endpoints

### Health Check

```
GET /api/v1/healthz
Response: { status: "ok", service: "marketplace-service", version: "15.3.0", timestamp: "ISO" }
```

**Note**: Version mismatch - healthz returns "15.3.0" but package.json shows "16.0.0"

---

### Marketplace Endpoints

#### Get Products

```
GET /api/v1/market/products
Auth: None
Query Parameters:
  - category?: string (ProductCategory)
  - governorate?: string
  - sellerId?: string
  - minPrice?: number
  - maxPrice?: number
  - page?: number
  - limit?: number

Response:
{
  data: Product[],
  pagination: {
    page: number,
    limit: number,
    total: number,
    totalPages: number
  }
}
```

#### Get Product by ID

```
GET /api/v1/market/products/:id
Auth: None
Params: id - Product UUID

Response: Product
```

#### Create Product

```
POST /api/v1/market/products
Auth: Required (JWT)

Request Body:
{
  name: string,           // English name
  nameAr: string,         // Arabic name
  category: string,       // ProductCategory enum
  price: number,          // Price per unit (YER)
  stock: number,          // Available quantity
  unit: string,           // "ton", "kg", "unit"
  description?: string,
  descriptionAr?: string,
  imageUrl?: string,
  sellerId: string,       // Required
  sellerType: string,     // SellerType enum
  sellerName?: string,
  cropType?: string,
  governorate?: string
}

Response: Product
```

#### List Harvest (Convert Yield Prediction to Product)

```
POST /api/v1/market/list-harvest
Auth: Required (JWT)

Request Body:
{
  userId: string,
  yieldData: {
    crop: string,
    cropAr: string,
    predictedYieldTons: number,
    pricePerTon: number,
    harvestDate?: string,
    qualityGrade?: string,  // "A", "B", "C"
    governorate?: string,
    district?: string
  }
}

Response: Product (auto-generated from yield data)
```

#### Create Order

```
POST /api/v1/market/orders
Auth: Required (JWT)

Request Body:
{
  buyerId: string,
  buyerName?: string,
  buyerPhone?: string,    // Yemeni phone format
  items: [{
    productId: string,
    quantity: number
  }],
  deliveryAddress?: string,
  paymentMethod?: string  // "wallet", "cash", "bank_transfer"
}

Response: Order with items

Note: Automatically calculates:
  - subtotal: sum of item prices
  - serviceFee: 2% of subtotal
  - deliveryFee: 500 YER (fixed)
  - totalAmount: subtotal + serviceFee + deliveryFee
```

#### Get User Orders

```
GET /api/v1/market/orders/:userId
Auth: Required (JWT) - Must be owner or admin
Query Parameters:
  - role?: "buyer" | "seller" (default: "buyer")

Response: PaginatedResponse<Order>
```

#### Get Market Statistics

```
GET /api/v1/market/stats
Auth: None

Response:
{
  totalProducts: number,
  totalHarvests: number,
  totalOrders: number,
  recentProducts: Product[]
}
```

---

### Wallet Endpoints

#### Get Wallet

```
GET /api/v1/fintech/wallet/:userId
Auth: None
Query Parameters:
  - userType?: string (default: "farmer")

Response: Wallet (creates if not exists)
{
  id: string,
  userId: string,
  userType: string,
  balance: number,
  escrowBalance: number,
  currency: string,
  creditScore: number,
  creditTier: string,
  creditTierAr: string,
  loanLimit: number,
  currentLoan: number,
  availableCredit: number,
  dailyWithdrawLimit: number,
  singleTransactionLimit: number,
  requiresPinForAmount: number,
  isVerified: boolean,
  kycStatus?: string
}
```

#### Deposit

```
POST /api/v1/fintech/wallet/:walletId/deposit
Auth: Required (JWT)

Request Body:
{
  amount: number,     // Must be > 0
  description?: string
}

Response:
{
  wallet: Wallet,
  transaction: Transaction,
  duplicate: boolean
}
```

#### Withdraw

```
POST /api/v1/fintech/wallet/:walletId/withdraw
Auth: Required (JWT)

Request Body:
{
  amount: number,     // Must be > 0
  description?: string
}

Response:
{
  wallet: Wallet,
  transaction: Transaction,
  duplicate: boolean
}

Errors:
- 400: "الرصيد غير كافي" (Insufficient balance)
- 400: "المبلغ يتجاوز حد المعاملة الواحدة" (Exceeds single transaction limit)
- 400: "تجاوزت حد السحب اليومي" (Exceeds daily withdraw limit)
```

#### Get Transactions

```
GET /api/v1/fintech/wallet/:walletId/transactions
Auth: None
Query Parameters:
  - limit?: number (default: 20)

Response: Transaction[]
```

#### Get Wallet Limits

```
GET /api/v1/fintech/wallet/:walletId/limits
Auth: None

Response:
{
  dailyWithdrawLimit: number,
  dailyRemaining: number,
  singleTransactionLimit: number,
  requiresPinForAmount: number,
  creditTier: string
}
```

#### Update Wallet Limits

```
PUT /api/v1/fintech/wallet/:walletId/limits
Auth: None (BUG: should require auth)

Response: Updated Wallet

Note: Updates limits based on credit tier:
- PLATINUM: daily=100000, single=500000, pin=50000
- GOLD: daily=50000, single=200000, pin=20000
- SILVER: daily=20000, single=100000, pin=10000
- BRONZE: daily=10000, single=50000, pin=5000
```

#### Get Wallet Dashboard

```
GET /api/v1/fintech/wallet/:walletId/dashboard
Auth: None

Response:
{
  wallet: { id, balance, escrowBalance, creditScore, creditTier, creditTierAr },
  summary: {
    totalBalance: number,
    inEscrowAsBuyer: number,
    inEscrowAsSeller: number,
    pendingPaymentsAmount: number,
    pendingPaymentsCount: number,
    availableCredit: number,
    currentLoan: number
  },
  limits: {
    dailyWithdrawLimit: number,
    dailyRemaining: number,
    singleTransactionLimit: number
  },
  monthlyChart: [{ date: string, income: number, expense: number }],
  recentTransactions: Transaction[]
}
```

---

### Credit Scoring Endpoints

#### Calculate Credit Score (Legacy)

```
POST /api/v1/fintech/calculate-score
Auth: Required (JWT)

Request Body:
{
  userId: string,
  farmData: {
    totalArea: number,           // Hectares
    activeSeasons: number,
    fieldCount: number,
    diseaseRisk: "Low" | "Medium" | "High",
    irrigationType: string,
    avgYieldScore: number,       // 0-100
    onTimePayments: number,
    latePayments: number
  }
}

Response:
{
  wallet: Wallet,
  scoreBreakdown: {
    assetsScore: number,
    experienceScore: number,
    riskScore: number,
    yieldScore: number
  },
  creditTierAr: string,
  availableCredit: number,
  message: string
}
```

#### Calculate Advanced Credit Score

```
POST /api/v1/fintech/calculate-advanced-score
Auth: Required (JWT)

Request Body:
{
  userId: string,
  factors: {
    farmArea: number,
    numberOfSeasons: number,
    diseaseRiskScore: number,    // 0-100
    irrigationType: "rainfed" | "drip" | "flood" | "sprinkler",
    yieldScore: number,          // 0-100
    paymentHistory: number,      // 0-100
    cropDiversity: number,       // 1-10
    marketplaceHistory: number,  // 0-100
    loanRepaymentRate: number,   // 0-100
    verificationLevel: "basic" | "verified" | "premium",
    landOwnership: "owned" | "leased" | "shared",
    cooperativeMember: boolean,
    yearsOfExperience: number,
    satelliteVerified: boolean
  }
}

Response:
{
  wallet: Wallet,
  score: number,
  creditTier: string,
  creditTierAr: string,
  loanLimit: number,
  availableCredit: number,
  breakdown: {
    farmDataScore: number,       // 40% weight
    paymentHistoryScore: number, // 30% weight
    verificationScore: number,   // 20% weight
    bonusScore: number           // 10% weight
  },
  factors: CreditFactors
}
```

#### Get Credit Factors

```
GET /api/v1/fintech/credit-factors/:userId
Auth: None

Response: CreditFactors
```

#### Record Credit Event

```
POST /api/v1/fintech/credit-history
Auth: Required (JWT)

Request Body:
{
  walletId: string,
  eventType: string,  // CreditEventType enum
  amount?: number,
  description: string,
  metadata?: object
}

Response:
{
  event: CreditEvent,
  wallet: Wallet,
  impact: number,
  message: string
}

Event Types & Impact:
- LOAN_REPAID_ONTIME: +15
- LOAN_REPAID_LATE: -10
- LOAN_DEFAULTED: -50
- ORDER_COMPLETED: +5
- ORDER_CANCELLED: -5
- VERIFICATION_UPGRADE: +30
- FARM_VERIFIED: +20
- COOPERATIVE_JOINED: +10
- LAND_VERIFIED: +15
```

#### Get Credit Report

```
GET /api/v1/fintech/credit-report/:userId
Auth: None

Response:
{
  userId: string,
  currentScore: number,
  creditTier: string,
  factors: CreditFactors,
  scoreBreakdown: {
    farmDataScore: number,
    paymentHistoryScore: number,
    verificationScore: number,
    bonusScore: number
  },
  recommendations: [{
    action: string,
    impact: number,
    priority: "high" | "medium" | "low",
    category: string
  }],
  recentEvents: CreditEvent[],
  availableCredit: number,
  riskLevel: "low" | "medium" | "high"
}
```

---

### Loan Endpoints

#### Request Loan

```
POST /api/v1/fintech/loans
Auth: Required (JWT)

Request Body:
{
  walletId: string,
  amount: number,        // Must not exceed available credit
  termMonths: number,    // 1-60
  purpose: string,       // LoanPurpose enum
  purposeDetails?: string,
  collateralType?: string,
  collateralValue?: number
}

Response:
{
  loan: Loan,
  message: string,
  nextSteps: string[]
}

Note: totalDue = amount + (amount * 0.02) // 2% admin fee
```

#### Approve Loan (Admin)

```
PUT /api/v1/fintech/loans/:id/approve
Auth: Required (JWT) - Admin role required

Response:
{
  loan: Loan,
  wallet: Wallet,
  transaction: Transaction
}
```

#### Repay Loan

```
POST /api/v1/fintech/loans/:id/repay
Auth: Required (JWT)

Request Body:
{
  amount: number
}

Response:
{
  loan: Loan,
  wallet: Wallet,
  transaction: Transaction,
  remainingAmount: number,
  message: string,
  duplicate: boolean
}
```

#### Get User Loans

```
GET /api/v1/fintech/loans/:walletId
Auth: None

Response: Loan[]
```

#### Get Finance Statistics

```
GET /api/v1/fintech/stats
Auth: None

Response:
{
  totalWallets: number,
  totalBalance: number,
  activeLoans: number,
  paidLoans: number,
  avgCreditScore: number
}
```

---

### Escrow Endpoints

#### Create Escrow

```
POST /api/v1/fintech/escrow
Auth: Required (JWT)

Request Body:
{
  orderId: string,
  buyerWalletId: string,
  sellerWalletId: string,
  amount: number,
  notes?: string
}

Response:
{
  escrow: Escrow,
  wallet: Wallet,
  transaction: Transaction,
  duplicate: boolean
}
```

#### Release Escrow

```
POST /api/v1/fintech/escrow/:id/release
Auth: Required (JWT)

Request Body:
{
  notes?: string
}

Response:
{
  escrow: Escrow,
  buyerWallet: Wallet,
  sellerWallet: Wallet,
  transactions: Transaction[],
  duplicate: boolean
}
```

#### Refund Escrow

```
POST /api/v1/fintech/escrow/:id/refund
Auth: Required (JWT)

Request Body:
{
  reason?: string
}

Response:
{
  escrow: Escrow,
  wallet: Wallet,
  transaction: Transaction,
  duplicate: boolean
}
```

#### Get Escrow by Order

```
GET /api/v1/fintech/escrow/order/:orderId
Auth: None

Response: Escrow with buyer/seller wallets
```

#### Get Wallet Escrows

```
GET /api/v1/fintech/wallet/:walletId/escrows
Auth: None

Response:
{
  asBuyer: Escrow[],
  asSeller: Escrow[]
}
```

---

### Scheduled Payments Endpoints

#### Create Scheduled Payment

```
POST /api/v1/fintech/wallet/:walletId/scheduled-payment
Auth: None (BUG: should require auth)

Request Body:
{
  amount: number,
  frequency: string,    // PaymentFrequency enum
  nextPaymentDate: string,  // ISO date
  loanId?: string,
  description?: string,
  descriptionAr?: string
}

Response:
{
  scheduledPayment: ScheduledPayment,
  message: string
}
```

#### Get Scheduled Payments

```
GET /api/v1/fintech/wallet/:walletId/scheduled-payments
Auth: None
Query Parameters:
  - activeOnly?: boolean (default: true)

Response: ScheduledPayment[]
```

#### Cancel Scheduled Payment

```
POST /api/v1/fintech/scheduled-payment/:id/cancel
Auth: None (BUG: should require auth)

Response: ScheduledPayment (isActive: false)
```

#### Execute Scheduled Payment

```
POST /api/v1/fintech/scheduled-payment/:id/execute
Auth: None (BUG: should require auth)

Response:
{
  payment: ScheduledPayment,
  wallet: Wallet,
  transaction: Transaction
}
```

---

### Seller Profile Endpoints

#### Create Seller Profile

```
POST /api/v1/profiles/sellers
Auth: Required (JWT)

Request Body:
{
  userId: string,
  tenantId: string,
  businessName: string,
  businessType: BusinessType,
  taxId?: string,
  bankAccount?: object,
  payoutPreferences?: object
}

Response: SellerProfile
```

#### Get All Sellers

```
GET /api/v1/profiles/sellers
Auth: None
Query Parameters:
  - businessType?: BusinessType
  - verified?: boolean
  - tenantId?: string
  - minRating?: number

Response: SellerProfile[]
```

#### Get Seller by User ID

```
GET /api/v1/profiles/sellers/user/:userId
Auth: None

Response: SellerProfile with review responses
```

#### Get Seller by ID

```
GET /api/v1/profiles/sellers/:id
Auth: None

Response: SellerProfile with review responses
```

#### Update Seller Profile

```
PUT /api/v1/profiles/sellers/user/:userId
Auth: Required (JWT)

Request Body:
{
  businessName?: string,
  businessType?: BusinessType,
  taxId?: string,
  bankAccount?: object,
  payoutPreferences?: object
}

Response: SellerProfile
```

#### Verify Seller

```
PATCH /api/v1/profiles/sellers/user/:userId/verify
Auth: Required (JWT)

Request Body:
{
  verified: boolean
}

Response: SellerProfile
```

#### Update Seller Stats

```
PATCH /api/v1/profiles/sellers/user/:userId/stats
Auth: Required (JWT)

Request Body:
{
  saleAmount: number,
  incrementSales?: number
}

Response: SellerProfile
```

---

### Buyer Profile Endpoints

#### Create Buyer Profile

```
POST /api/v1/profiles/buyers
Auth: Required (JWT)

Request Body:
{
  userId: string,
  tenantId: string,
  shippingAddresses?: ShippingAddress[],
  preferredPayment?: string  // "wallet" | "cash" | "bank_transfer"
}

Response: BuyerProfile
```

#### Get All Buyers

```
GET /api/v1/profiles/buyers
Auth: None
Query Parameters:
  - tenantId?: string
  - minPurchases?: number
  - minLoyaltyPoints?: number

Response: BuyerProfile[]
```

#### Get Buyer by User ID

```
GET /api/v1/profiles/buyers/user/:userId
Auth: None

Response: BuyerProfile with reviews
```

#### Get Buyer by ID

```
GET /api/v1/profiles/buyers/:id
Auth: None

Response: BuyerProfile with reviews
```

#### Update Buyer Profile

```
PUT /api/v1/profiles/buyers/user/:userId
Auth: Required (JWT)

Request Body:
{
  shippingAddresses?: ShippingAddress[],
  preferredPayment?: string
}

Response: BuyerProfile
```

#### Add Shipping Address

```
POST /api/v1/profiles/buyers/user/:userId/addresses
Auth: Required (JWT)

Request Body:
{
  label: string,
  address: string,
  city: string,
  phone?: string,
  isDefault?: boolean
}

Response: BuyerProfile
```

#### Remove Shipping Address

```
DELETE /api/v1/profiles/buyers/user/:userId/addresses/:label
Auth: Required (JWT)

Response: BuyerProfile
```

#### Update Loyalty Points

```
PATCH /api/v1/profiles/buyers/user/:userId/loyalty-points
Auth: Required (JWT)

Request Body:
{
  points: number,  // Can be negative
  reason?: string
}

Response: BuyerProfile
```

#### Update Buyer Stats

```
PATCH /api/v1/profiles/buyers/user/:userId/stats
Auth: Required (JWT)

Request Body:
{
  purchaseAmount: number,
  incrementPurchases?: number
}

Response: BuyerProfile
Note: Awards 1 loyalty point per 100 YER spent
```

---

### Review Endpoints

#### Create Product Review

```
POST /api/v1/reviews
Auth: Required (JWT)

Request Body:
{
  productId: string,
  buyerId: string,    // Buyer profile ID
  orderId: string,
  rating: number,     // 1-5
  title: string,
  comment?: string,
  photos?: string[]   // URLs
}

Response: ProductReview with buyer
Note: verified = true if order status is DELIVERED
```

#### Get Product Reviews

```
GET /api/v1/reviews/product/:productId
Auth: None
Query Parameters:
  - minRating?: number (1-5)
  - maxRating?: number (1-5)
  - verified?: boolean
  - limit?: number (default: 20, max: 100)
  - offset?: number (default: 0)

Response:
{
  reviews: ProductReview[],
  stats: {
    totalReviews: number,
    averageRating: number,
    ratingDistribution: { 1: n, 2: n, 3: n, 4: n, 5: n }
  },
  pagination: { limit, offset }
}
```

#### Get Product Review Stats

```
GET /api/v1/reviews/product/:productId/stats
Auth: None

Response:
{
  totalReviews: number,
  averageRating: number,
  ratingDistribution: { 1: n, 2: n, 3: n, 4: n, 5: n }
}
```

#### Get Review by ID

```
GET /api/v1/reviews/:id
Auth: None

Response: ProductReview with buyer and response
```

#### Get Buyer Reviews

```
GET /api/v1/reviews/buyer/:buyerId
Auth: None
Query Parameters:
  - limit?: number
  - offset?: number

Response: ProductReview[]
```

#### Update Product Review

```
PUT /api/v1/reviews/:id/buyer/:buyerId
Auth: Required (JWT)

Request Body:
{
  rating?: number,
  title?: string,
  comment?: string,
  photos?: string[]
}

Response: ProductReview
Error: 403 if not owner
```

#### Delete Product Review

```
DELETE /api/v1/reviews/:id/buyer/:buyerId
Auth: Required (JWT)

Response: { message: "Review deleted successfully" }
Error: 403 if not owner
```

#### Mark Review Helpful

```
PATCH /api/v1/reviews/:id/helpful
Auth: Required (JWT)

Request Body:
{
  helpful: boolean  // true = +1, false = -1
}

Response: ProductReview
```

#### Report Review

```
POST /api/v1/reviews/:id/report
Auth: Required (JWT)

Request Body:
{
  reason: string
}

Response: ProductReview (reported: true)
```

#### Create Review Response (Seller)

```
POST /api/v1/reviews/responses
Auth: Required (JWT)

Request Body:
{
  reviewId: string,
  sellerId: string,   // Seller profile ID
  response: string
}

Response: ReviewResponse with review and seller
```

#### Get Seller Responses

```
GET /api/v1/reviews/responses/seller/:sellerId
Auth: None
Query Parameters:
  - limit?: number
  - offset?: number

Response: ReviewResponse[]
```

#### Update Review Response

```
PUT /api/v1/reviews/responses/:id/seller/:sellerId
Auth: Required (JWT)

Request Body:
{
  response: string
}

Response: ReviewResponse
Error: 403 if not owner
```

#### Delete Review Response

```
DELETE /api/v1/reviews/responses/:id/seller/:sellerId
Auth: Required (JWT)

Response: { message: "Review response deleted successfully" }
Error: 403 if not owner
```

---

## NATS Events

### Events Published

| Event Subject | Description | Payload |
|---------------|-------------|---------|
| `order.placed` | Order created | `{ orderId, userId, items[], totalAmount, currency }` |
| `order.completed` | Order delivered | `{ orderId, userId, completedAt, totalAmount, currency }` |
| `order.cancelled` | Order cancelled | `{ orderId, userId, cancelledAt, reason? }` |
| `inventory.low_stock` | Stock below threshold | `{ productId, productName, currentStock, threshold, unit }` |
| `inventory.movement` | Stock changed | `{ movementId, productId, quantity, movementType, ... }` |

### Event Payload Examples

```typescript
// order.placed
{
  eventId: "uuid",
  eventType: "order.placed",
  timestamp: "2025-01-25T10:00:00Z",
  version: "1.0",
  metadata: { source: "marketplace-service" },
  payload: {
    orderId: "order-uuid",
    userId: "user-uuid",
    items: [{ productId: "prod-uuid", quantity: 10, price: 1500 }],
    totalAmount: 15000,
    currency: "YER"
  }
}

// inventory.low_stock
{
  eventId: "uuid",
  eventType: "inventory.low_stock",
  timestamp: "2025-01-25T10:00:00Z",
  payload: {
    productId: "prod-uuid",
    productName: "قمح عالي الجودة",
    currentStock: 8,
    threshold: 10,
    unit: "ton"
  }
}
```

### Events Subscribed

Currently, the service does not subscribe to any external events.

---

## Dependencies

### Internal Services

| Service | Purpose |
|---------|---------|
| PostgreSQL | Primary database |
| NATS | Event messaging (optional, degraded mode if unavailable) |
| Redis | Token revocation via `@sahool/nestjs-auth`, caching |

### External APIs

None directly. The service is designed to be self-contained.

### NPM Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| @nestjs/core | ^10.4.15 | NestJS framework |
| @nestjs/swagger | ^8.1.0 | API documentation |
| @nestjs/throttler | ^6.2.1 | Rate limiting |
| @prisma/client | ^5.22.0 | Database ORM |
| class-validator | ^0.14.1 | DTO validation |
| jsonwebtoken | ^9.0.2 | JWT authentication |
| nats | ^2.28.2 | Event messaging |
| uuid | ^10.0.0 | UUID generation |

---

## Bugs, Issues & Recommended Fixes

### Critical Bugs

1. **Version Mismatch**
   - File: `src/app.controller.ts` line 58
   - Issue: healthz returns "15.3.0" but package.json shows "16.0.0"
   - Fix: Update version to "16.0.0"

2. **Missing Authentication on Critical Endpoints**
   - File: `src/app.controller.ts`
   - Affected endpoints:
     - `PUT /fintech/wallet/:walletId/limits` (line 354)
     - `POST /fintech/wallet/:walletId/scheduled-payment` (line 440)
     - `POST /fintech/scheduled-payment/:id/cancel` (line 485)
     - `POST /fintech/scheduled-payment/:id/execute` (line 493)
   - Issue: These financial endpoints lack `@UseGuards(JwtAuthGuard)`
   - Fix: Add `@UseGuards(JwtAuthGuard)` decorator

3. **Missing Resource Ownership Validation**
   - File: `src/app.controller.ts`
   - Affected endpoints: All wallet operations except getUserOrders
   - Issue: Users can access/modify other users' wallets
   - Fix: Add ownership validation similar to getUserOrders

### Medium Bugs

4. **Hardcoded Business Logic Values**
   - Files: `market.service.ts`, `fintech.service.ts`, `loan.service.ts`
   - Issues:
     - Service fee: 2% hardcoded
     - Delivery fee: 500 YER hardcoded
     - Loan admin fee: 2% hardcoded
     - Low stock threshold: 10 hardcoded
   - Fix: Move to environment variables

5. **NATS Connection Not Auto-Initialized**
   - File: `src/events/events.service.ts`
   - Issue: `connect()` is never called automatically
   - Fix: Add `OnModuleInit` hook to call `connect()`

6. **Transaction Isolation Not Consistent**
   - Some financial operations use `Serializable`, others don't
   - File: `loan.service.ts` - `approveLoan` and `executeScheduledPayment`
   - Fix: Use consistent isolation level for all financial transactions

### Low Priority Issues

7. **Missing Pagination on Several Endpoints**
   - `GET /fintech/wallet/:walletId/escrows`
   - `GET /fintech/loans/:walletId`
   - Fix: Add pagination parameters

8. **No Input Sanitization for Log Injection**
   - Most logging doesn't sanitize user input
   - EventsService has `sanitizeForLog` but not used everywhere
   - Fix: Apply consistently

9. **Missing API Rate Limiting on Some Endpoints**
   - Only healthz has explicit rate limiting
   - Fix: Add rate limiting to financial endpoints

---

## Admin Portal Integration Notes

### Required Pages

1. **Dashboard**
   - API: `GET /api/v1/market/stats`, `GET /api/v1/fintech/stats`
   - Display: Product count, order count, wallet stats, loan stats

2. **Products Management**
   - APIs: `GET /api/v1/market/products`, `POST /api/v1/market/products`
   - Features: List, filter, create products

3. **Orders Management**
   - API: Custom admin endpoint needed (not currently exposed)
   - Note: getUserOrders is user-scoped, need admin endpoint

4. **Wallets Management**
   - API: `GET /api/v1/fintech/wallet/:userId`
   - Features: View wallet details, credit scores

5. **Loans Management**
   - APIs: `GET /api/v1/fintech/loans/:walletId`, `PUT /api/v1/fintech/loans/:id/approve`
   - Features: List pending loans, approve/reject

6. **Credit Reports**
   - API: `GET /api/v1/fintech/credit-report/:userId`
   - Features: View credit breakdown, recommendations

7. **Seller Verification**
   - APIs: `GET /api/v1/profiles/sellers`, `PATCH /api/v1/profiles/sellers/user/:userId/verify`
   - Features: List sellers, verify/unverify

8. **Reviews Moderation**
   - API: Custom admin endpoint needed
   - Note: Reviews have `reported: true` flag for moderation

### Missing Admin Endpoints (Need to Add)

```typescript
// Suggested additions:
GET /api/v1/admin/orders                    // All orders with filters
GET /api/v1/admin/wallets                   // All wallets with filters
GET /api/v1/admin/loans                     // All loans with filters
GET /api/v1/admin/reviews/reported          // Reported reviews
PATCH /api/v1/admin/reviews/:id/moderate    // Approve/remove reported reviews
GET /api/v1/admin/escrows                   // All escrows with filters
POST /api/v1/admin/escrows/:id/dispute      // Mark escrow as disputed
```

### Authentication Notes

- Admin endpoints should check `request.user.roles.includes('admin')`
- Current implementation in `jwt-auth.guard.ts` extracts roles from JWT
- JWT payload expected format: `{ sub, email, roles: string[], tenant_id }`

---

## Rate Limiting Configuration

```typescript
// Current configuration in app.module.ts
ThrottlerModule.forRoot([
  { name: "short", ttl: 1000, limit: 10 },    // 10 req/sec
  { name: "medium", ttl: 60000, limit: 100 }, // 100 req/min
  { name: "long", ttl: 3600000, limit: 1000 } // 1000 req/hour
])
```

---

## Swagger Documentation

- Available at: `http://localhost:3010/docs`
- Tags: Market, Wallet, Loans, Seller Profiles, Buyer Profiles, Product Reviews

---

## Docker Health Check

```
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3010/api/v1/healthz || exit 1
```
