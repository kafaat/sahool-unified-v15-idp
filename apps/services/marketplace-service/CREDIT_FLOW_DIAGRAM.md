# Credit Scoring System Flow Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SAHOOL CREDIT SCORING SYSTEM                     │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA COLLECTION                               │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
    │ Farm Data    │      │ Payment      │      │ Verification │
    │ Services     │      │ History      │      │ Events       │
    └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
           │                     │                     │
           └──────────┬──────────┴──────────┬──────────┘
                      │                     │
                      ▼                     ▼
              ┌───────────────┐    ┌────────────────┐
              │ CreditFactors │    │ CreditEvent    │
              │   Interface   │    │     Table      │
              └───────┬───────┘    └────────┬───────┘
                      │                     │
                      └──────────┬──────────┘
                                 │
                                 ▼

┌─────────────────────────────────────────────────────────────────────────┐
│                      CREDIT SCORING ENGINE                              │
└─────────────────────────────────────────────────────────────────────────┘

                    calculateAdvancedCreditScore()
                                 │
                 ┌───────────────┼───────────────┐
                 │               │               │
                 ▼               ▼               ▼
         ┌──────────┐    ┌──────────┐    ┌──────────┐
         │ Farm     │    │ Payment  │    │ Verify   │
         │ Data 40% │    │ History  │    │ Trust    │
         │ 340 pts  │    │ 30%      │    │ 20%      │
         └────┬─────┘    │ 255 pts  │    │ 170 pts  │
              │          └────┬─────┘    └────┬─────┘
              │               │               │
              └───────┬───────┴───────┬───────┘
                      │               │
                      ▼               ▼
              ┌──────────┐    ┌──────────┐
              │ Bonus    │    │ TOTAL    │
              │ 10%      │───▶│ SCORE    │
              │ 85 pts   │    │ 300-850  │
              └──────────┘    └────┬─────┘
                                   │
                                   ▼

┌─────────────────────────────────────────────────────────────────────────┐
│                         CREDIT TIER ASSIGNMENT                          │
└─────────────────────────────────────────────────────────────────────────┘

                        Score Evaluation
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
    ┌───────▼──────┐    ┌───────▼──────┐    ┌───────▼──────┐
    │ 750-850      │    │ 650-749      │    │ 500-649      │
    │ PLATINUM     │    │ GOLD         │    │ SILVER       │
    │ 50x multi    │    │ 35x multi    │    │ 20x multi    │
    └──────────────┘    └──────────────┘    └──────────────┘
                                                     │
                                             ┌───────▼──────┐
                                             │ 300-499      │
                                             │ BRONZE       │
                                             │ 10x multi    │
                                             └──────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                      RECOMMENDATION ENGINE                              │
└─────────────────────────────────────────────────────────────────────────┘

                    generateRecommendations()
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
    ┌───────▼──────┐    ┌───────▼──────┐    ┌───────▼──────┐
    │ Analyze      │    │ Calculate    │    │ Prioritize   │
    │ Gaps         │───▶│ Impact       │───▶│ & Sort       │
    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                    │
                                            ┌───────▼───────┐
                                            │ Top 5 Actions │
                                            │ • High        │
                                            │ • Medium      │
                                            │ • Low         │
                                            └───────────────┘
```

---

## Credit Event Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        EVENT RECORDING FLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

    User Action (e.g., Loan Repayment)
                │
                ▼
    ┌───────────────────────┐
    │ recordCreditEvent()   │
    │                       │
    │ Input:                │
    │ • walletId            │
    │ • eventType           │
    │ • amount              │
    │ • description         │
    │ • metadata            │
    └──────────┬────────────┘
               │
               ▼
    ┌───────────────────────┐
    │ Determine Impact      │
    │                       │
    │ LOAN_REPAID_ONTIME    │───▶ +15 points
    │ LOAN_REPAID_LATE      │───▶ -10 points
    │ LOAN_DEFAULTED        │───▶ -50 points
    │ ORDER_COMPLETED       │───▶ +5 points
    │ FARM_VERIFIED         │───▶ +20 points
    │ COOPERATIVE_JOINED    │───▶ +10 points
    │ LAND_VERIFIED         │───▶ +15 points
    └──────────┬────────────┘
               │
               ▼
    ┌───────────────────────┐
    │ Create CreditEvent    │
    │ Record in Database    │
    └──────────┬────────────┘
               │
               ▼
    ┌───────────────────────┐
    │ Update Wallet         │
    │                       │
    │ newScore = oldScore   │
    │          + impact     │
    │                       │
    │ Recalculate Tier:     │
    │ ≥750 → PLATINUM       │
    │ ≥650 → GOLD           │
    │ ≥500 → SILVER         │
    │ else → BRONZE         │
    └──────────┬────────────┘
               │
               ▼
    ┌───────────────────────┐
    │ Return Response       │
    │                       │
    │ • Updated event       │
    │ • Updated wallet      │
    │ • Impact value        │
    │ • Success message     │
    └───────────────────────┘
```

---

## API Request Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TYPICAL USER JOURNEY                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌────────────────┐
│ 1. New Farmer  │
│    Registers   │
└───────┬────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ GET /fintech/wallet/:userId         │
│ → Auto-creates wallet               │
│ → Initial score: 300 (BRONZE)       │
└───────┬─────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ POST /fintech/credit-history        │
│ Body: { eventType: FARM_VERIFIED }  │
│ → Score: 300 + 20 = 320             │
└───────┬─────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│ Farmer completes 5 orders...        │
│ → 5 × ORDER_COMPLETED events        │
│ → Score: 320 + 25 = 345             │
└───────┬─────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ GET /fintech/credit-report/:userId   │
│ → Current score: 345                 │
│ → Tier: BRONZE                       │
│ → Recommendations:                   │
│   1. Verify land ownership (+35)     │
│   2. Upgrade verification (+30)      │
│   3. Join cooperative (+10)          │
└───────┬──────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ Farmer takes action on #1...         │
│ POST /fintech/credit-history         │
│ Body: { eventType: LAND_VERIFIED }   │
│ → Score: 345 + 15 = 360              │
└───────┬──────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────┐
│ After 6 months...                            │
│ POST /fintech/calculate-advanced-score       │
│ Body: { improved factors }                   │
│ → Farm area: 2→3 hectares                    │
│ → Crop diversity: 1→4 crops                  │
│ → Marketplace history: 5→20 orders           │
│ → Verification: basic→verified               │
│ → Land: leased→owned                         │
│ → Cooperative: false→true                    │
│                                              │
│ Result: Score 550 (SILVER) 🎉                │
│ Loan limit: 11,000 YER                       │
└──────────────────────────────────────────────┘
```

---

## Data Model Relationships

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATABASE SCHEMA                                 │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────┐
    │          Wallet                  │
    ├──────────────────────────────────┤
    │ id (PK)                          │
    │ userId (unique)                  │
    │ creditScore (300-850)            │◀─────┐
    │ creditTier (enum)                │      │
    │ loanLimit                        │      │
    │ currentLoan                      │      │
    │ balance                          │      │
    └─────────┬────────────────────────┘      │
              │                               │
              │ 1:N                           │
              │                               │
              ▼                               │
    ┌──────────────────────────────────┐     │
    │       CreditEvent                │     │
    ├──────────────────────────────────┤     │
    │ id (PK)                          │     │
    │ walletId (FK) ───────────────────┼─────┘
    │ eventType (enum)                 │
    │ amount                           │
    │ impact (-50 to +50)              │
    │ description                      │
    │ metadata (JSON)                  │
    │ createdAt                        │
    └──────────────────────────────────┘

    CreditEventType Enum:
    ┌──────────────────────┬────────┐
    │ LOAN_REPAID_ONTIME   │  +15   │
    │ LOAN_REPAID_LATE     │  -10   │
    │ LOAN_DEFAULTED       │  -50   │
    │ ORDER_COMPLETED      │  +5    │
    │ ORDER_CANCELLED      │  -5    │
    │ VERIFICATION_UPGRADE │  +30   │
    │ FARM_VERIFIED        │  +20   │
    │ COOPERATIVE_JOINED   │  +10   │
    │ LAND_VERIFIED        │  +15   │
    └──────────────────────┴────────┘
```

---

## Score Calculation Formula

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SCORING FORMULA BREAKDOWN                            │
└─────────────────────────────────────────────────────────────────────────┘

TOTAL SCORE = BASE + FARM + PAYMENT + VERIFICATION + BONUS

where:

BASE = 300 (minimum score)

FARM (max 340 points, 40%) =
    farmAreaPoints        (0-100)
  + cropDiversityPoints   (0-60)
  + experiencePoints      (0-80)
  + irrigationPoints      (0-50)
  + diseaseRiskPoints     (0-50)

PAYMENT (max 255 points, 30%) =
    paymentHistory        (0-100)
  + loanRepaymentRate     (0-100)
  + marketplaceHistory    (0-55)

VERIFICATION (max 170 points, 20%) =
    verificationLevel     (0-70)
  + landOwnership         (0-50)
  + satelliteVerified     (0-50)

BONUS (max 85 points, 10%) =
    cooperativeMember     (0-40)
  + yieldPerformance      (0-45)

────────────────────────────────────────────────────────────────────

Maximum Possible Score:
  300 (base)
+ 340 (farm)
+ 255 (payment)
+ 170 (verification)
+  85 (bonus)
─────────────────
= 850 points

Minimum Score: 300 points
```

---

## Recommendation Priority Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  RECOMMENDATION DECISION TREE                           │
└─────────────────────────────────────────────────────────────────────────┘

                    Analyze Credit Factors
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    Not Done?          Below Target?        Can Improve?
        │                   │                   │
        │                   │                   │
    ┌───▼────┐          ┌───▼────┐          ┌───▼────┐
    │ HIGH   │          │ MEDIUM │          │ LOW    │
    │ 30-35  │          │ 15-25  │          │ 10-12  │
    │ points │          │ points │          │ points │
    └────────┘          └────────┘          └────────┘

Examples:

HIGH Priority (Not Done + High Impact):
  ☐ Land not verified       → +35 points
  ☐ Account not premium     → +30 points
  ☐ Farm not satellite      → +20 points

MEDIUM Priority (Below Target):
  ☐ Repayment rate < 90%    → +20 points
  ☐ Orders < 5              → +15 points
  ☐ Poor irrigation         → +25 points

LOW Priority (Can Improve):
  ☐ Crop diversity < 3      → +12 points
  ☐ No cooperative          → +10 points
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SERVICE INTEGRATION MAP                              │
└─────────────────────────────────────────────────────────────────────────┘

    External Services          Marketplace Service       Database
    ─────────────────          ───────────────────       ────────

┌───────────────┐
│ farm-core     │──────┐
│ • farmArea    │      │
│ • ownership   │      │
└───────────────┘      │
                       │
┌───────────────┐      │        ┌──────────────┐      ┌──────────┐
│ field-core    │──────┼───────▶│ fintech      │─────▶│ Wallet   │
│ • seasons     │      │        │ service      │      │ Table    │
│ • diversity   │      │        │              │      └──────────┘
└───────────────┘      │        │ calculate    │
                       │        │ Advanced     │      ┌──────────┐
┌───────────────┐      │        │ CreditScore  │─────▶│ Credit   │
│ crop-health   │──────┤        │              │      │ Event    │
│ • disease     │      │        └──────────────┘      │ Table    │
└───────────────┘      │                              └──────────┘
                       │
┌───────────────┐      │
│ yield-engine  │──────┤
│ • yieldScore  │      │
└───────────────┘      │
                       │
┌───────────────┐      │
│ satellite     │──────┘
│ • verified    │
└───────────────┘

        Future: Real-time data sync
        Current: Default values + manual updates
```

This architecture supports:

- Modular integration
- Gradual service connection
- Fallback to defaults
- Future real-time sync
