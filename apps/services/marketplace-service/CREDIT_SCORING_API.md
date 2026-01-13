# Advanced Credit Scoring System - API Documentation

## Overview

The enhanced credit scoring system uses multiple factors to calculate a farmer's creditworthiness (300-850 points).

## Score Breakdown

- **Farm Data (40%)**: 340 points max
  - Farm area, crop diversity, experience, irrigation, disease risk
- **Payment History (30%)**: 255 points max
  - Payment history, loan repayment rate, marketplace orders
- **Verification (20%)**: 170 points max
  - Verification level, land ownership, satellite verification
- **Bonus Factors (10%)**: 85 points max
  - Cooperative membership, yield performance

## Credit Tiers

- **BRONZE** (300-499): 10x multiplier = up to 4,990 YER loan limit
- **SILVER** (500-649): 20x multiplier = up to 12,980 YER loan limit
- **GOLD** (650-749): 35x multiplier = up to 26,215 YER loan limit
- **PLATINUM** (750-850): 50x multiplier = up to 42,500 YER loan limit

---

## API Endpoints

### 1. Calculate Advanced Credit Score

**POST** `/api/v1/fintech/calculate-advanced-score`

Calculate credit score using the enhanced algorithm with all factors.

**Request Body:**

```json
{
  "userId": "user-123",
  "factors": {
    "farmArea": 5.5,
    "numberOfSeasons": 4,
    "diseaseRiskScore": 85,
    "irrigationType": "drip",
    "yieldScore": 88,
    "paymentHistory": 95,
    "cropDiversity": 4,
    "marketplaceHistory": 12,
    "loanRepaymentRate": 100,
    "verificationLevel": "verified",
    "landOwnership": "owned",
    "cooperativeMember": true,
    "yearsOfExperience": 5,
    "satelliteVerified": true
  }
}
```

**Response:**

```json
{
  "wallet": {
    "id": "wallet-456",
    "userId": "user-123",
    "creditScore": 752,
    "creditTier": "PLATINUM",
    "loanLimit": 37600,
    "balance": 5000,
    "currentLoan": 0
  },
  "score": 752,
  "creditTier": "PLATINUM",
  "creditTierAr": "بلاتيني",
  "loanLimit": 37600,
  "availableCredit": 37600,
  "breakdown": {
    "farmDataScore": 310,
    "paymentHistoryScore": 240,
    "verificationScore": 170,
    "bonusScore": 80
  },
  "factors": { ... }
}
```

---

### 2. Get Credit Factors

**GET** `/api/v1/fintech/credit-factors/:userId`

Retrieve detailed credit factors for a user calculated from their wallet data and credit events.

**Example:** `GET /api/v1/fintech/credit-factors/user-123`

**Response:**

```json
{
  "farmArea": 5,
  "numberOfSeasons": 3,
  "diseaseRiskScore": 75,
  "irrigationType": "drip",
  "yieldScore": 80,
  "paymentHistory": 100,
  "cropDiversity": 3,
  "marketplaceHistory": 8,
  "loanRepaymentRate": 85.7,
  "verificationLevel": "verified",
  "landOwnership": "leased",
  "cooperativeMember": false,
  "yearsOfExperience": 3,
  "satelliteVerified": true
}
```

---

### 3. Record Credit Event

**POST** `/api/v1/fintech/credit-history`

Record a credit event that impacts the user's credit score.

**Request Body:**

```json
{
  "walletId": "wallet-456",
  "eventType": "LOAN_REPAID_ONTIME",
  "amount": 5000,
  "description": "سداد قرض شراء بذور في الموعد",
  "metadata": {
    "loanId": "loan-789",
    "daysEarly": 2
  }
}
```

**Event Types & Impact:**
| Event Type | Impact | Description |
|------------|--------|-------------|
| `LOAN_REPAID_ONTIME` | +15 | Loan repaid on time |
| `LOAN_REPAID_LATE` | -10 | Loan repaid late |
| `LOAN_DEFAULTED` | -50 | Loan defaulted |
| `ORDER_COMPLETED` | +5 | Marketplace order completed |
| `ORDER_CANCELLED` | -5 | Order cancelled |
| `VERIFICATION_UPGRADE` | +30 | Account verification upgraded |
| `FARM_VERIFIED` | +20 | Farm verified by satellite |
| `COOPERATIVE_JOINED` | +10 | Joined agricultural cooperative |
| `LAND_VERIFIED` | +15 | Land ownership verified |

**Response:**

```json
{
  "event": {
    "id": "event-001",
    "walletId": "wallet-456",
    "eventType": "LOAN_REPAID_ONTIME",
    "amount": 5000,
    "impact": 15,
    "description": "سداد قرض شراء بذور في الموعد",
    "createdAt": "2025-12-25T10:30:00Z"
  },
  "wallet": {
    "id": "wallet-456",
    "creditScore": 535,
    "creditTier": "SILVER"
  },
  "impact": 15,
  "message": "رائع! ارتفع تصنيفك الائتماني بمقدار 15 نقطة"
}
```

---

### 4. Get Credit Report

**GET** `/api/v1/fintech/credit-report/:userId`

Get a comprehensive credit report with score breakdown, factors, recommendations, and recent events.

**Example:** `GET /api/v1/fintech/credit-report/user-123`

**Response:**

```json
{
  "userId": "user-123",
  "currentScore": 625,
  "creditTier": "فضي",
  "factors": {
    "farmArea": 5,
    "cropDiversity": 3,
    "marketplaceHistory": 8,
    "loanRepaymentRate": 85.7,
    "verificationLevel": "verified",
    "landOwnership": "leased",
    "cooperativeMember": false,
    "satelliteVerified": true,
    ...
  },
  "scoreBreakdown": {
    "farmDataScore": 250,
    "paymentHistoryScore": 187,
    "verificationScore": 125,
    "bonusScore": 63
  },
  "recommendations": [
    {
      "action": "وثق ملكية الأرض لزيادة تصنيفك",
      "impact": 35,
      "priority": "high",
      "category": "verification"
    },
    {
      "action": "قم برفع مستوى التحقق من حسابك إلى \"موثق\"",
      "impact": 30,
      "priority": "high",
      "category": "verification"
    },
    {
      "action": "حافظ على سداد القروض في الوقت المحدد",
      "impact": 20,
      "priority": "high",
      "category": "payment"
    },
    {
      "action": "أكمل 2 طلبات إضافية في السوق",
      "impact": 15,
      "priority": "medium",
      "category": "activity"
    },
    {
      "action": "انضم إلى تعاونية زراعية لزيادة مصداقيتك",
      "impact": 10,
      "priority": "medium",
      "category": "trust"
    }
  ],
  "recentEvents": [
    {
      "id": "event-003",
      "eventType": "ORDER_COMPLETED",
      "impact": 5,
      "description": "إتمام بيع محصول طماطم",
      "createdAt": "2025-12-20T14:22:00Z"
    },
    {
      "id": "event-002",
      "eventType": "FARM_VERIFIED",
      "impact": 20,
      "description": "التحقق من المزرعة عبر الأقمار الصناعية",
      "createdAt": "2025-12-15T09:15:00Z"
    }
  ],
  "availableCredit": 12500,
  "riskLevel": "medium"
}
```

---

## Usage Examples

### Example 1: New Farmer Onboarding

```javascript
// 1. Create wallet (automatic on first access)
const wallet = await GET("/api/v1/fintech/wallet/new-farmer-001");

// 2. Record farm verification
await POST("/api/v1/fintech/credit-history", {
  walletId: wallet.id,
  eventType: "FARM_VERIFIED",
  description: "Farm verified via satellite imagery",
});

// 3. Calculate initial credit score
const score = await POST("/api/v1/fintech/calculate-advanced-score", {
  userId: "new-farmer-001",
  factors: {
    farmArea: 2.5,
    cropDiversity: 2,
    irrigationType: "rainfed",
    yearsOfExperience: 1,
    verificationLevel: "verified",
    landOwnership: "leased",
    satelliteVerified: true,
    // ... other factors with defaults
  },
});

console.log(`Credit Score: ${score.score}`);
console.log(`Available Credit: ${score.availableCredit} YER`);
```

### Example 2: Processing Loan Repayment

```javascript
// When a loan is repaid on time
await POST("/api/v1/fintech/credit-history", {
  walletId: "wallet-456",
  eventType: "LOAN_REPAID_ONTIME",
  amount: 10000,
  description: "Repaid fertilizer purchase loan on time",
  metadata: {
    loanId: "loan-789",
    originalDueDate: "2025-12-25",
    paidDate: "2025-12-23",
  },
});

// Score automatically increases by +15 points
```

### Example 3: Generating Credit Improvement Plan

```javascript
// Get comprehensive credit report
const report = await GET("/api/v1/fintech/credit-report/farmer-123");

console.log(`Current Score: ${report.currentScore}`);
console.log(`Risk Level: ${report.riskLevel}`);
console.log("\nTop Recommendations:");

report.recommendations.forEach((rec, i) => {
  console.log(`${i + 1}. [+${rec.impact}] ${rec.action}`);
  console.log(`   Priority: ${rec.priority} | Category: ${rec.category}`);
});
```

### Example 4: Cooperative Verification

```javascript
// When farmer joins a cooperative
await POST("/api/v1/fintech/credit-history", {
  walletId: "wallet-456",
  eventType: "COOPERATIVE_JOINED",
  description: "Joined Al-Khayr Agricultural Cooperative",
  metadata: {
    cooperativeId: "coop-001",
    cooperativeName: "تعاونية الخير الزراعية",
    joinDate: "2025-12-25",
  },
});

// Score increases by +10 points
```

---

## Integration Notes

### Automatic Credit Events

The system should automatically record credit events when:

- An order is completed → `ORDER_COMPLETED` (+5)
- An order is cancelled → `ORDER_CANCELLED` (-5)
- A loan is repaid on time → `LOAN_REPAID_ONTIME` (+15)
- A loan is repaid late → `LOAN_REPAID_LATE` (-10)
- A loan defaults → `LOAN_DEFAULTED` (-50)

### Pulling Farm Data from Other Services

The `getCreditFactors` method currently uses default values. In production, integrate with:

- **farm-core**: Get actual `farmArea`, `landOwnership`
- **field-core**: Get `numberOfSeasons`, `cropDiversity`
- **crop-health-ai**: Get `diseaseRiskScore`
- **yield-engine**: Get `yieldScore`
- **satellite-service**: Verify `satelliteVerified` status

### Database Migration

After deploying, run:

```bash
cd apps/services/marketplace-service
npx prisma migrate dev --name add_credit_events
npx prisma generate
```

---

## Security Considerations

1. **Credit Event Validation**: Only authorized services should record credit events
2. **Score Manipulation**: Credit score changes should be logged and auditable
3. **Privacy**: Credit reports contain sensitive information - implement proper access control
4. **Rate Limiting**: Prevent abuse of credit score calculation endpoints

---

## Monitoring & Analytics

Track these metrics:

- Average credit score by region
- Credit tier distribution
- Most impactful credit events
- Time to improve from BRONZE to SILVER
- Loan default rates by credit tier
- Recommendation completion rates

---

## Future Enhancements

1. **Machine Learning**: Train models on historical data to predict default risk
2. **Social Credit**: Factor in peer reviews and community reputation
3. **Seasonal Adjustments**: Adjust scoring based on agricultural seasons
4. **Multi-Factor Authentication**: Require MFA for high-value credit decisions
5. **Credit Score History**: Track score changes over time with charts
6. **A/B Testing**: Test different scoring formulas to optimize loan repayment rates
