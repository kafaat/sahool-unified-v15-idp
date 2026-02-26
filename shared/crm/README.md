# shared/crm - Farmer CRM Module

وحدة إدارة علاقات المزارعين

Agricultural customer relationship management system inspired by CordysCRM architecture, adapted for farmer lifecycle management, harvest deal pipelines, and interaction tracking.

## File Structure

```
shared/crm/
├── __init__.py       # Package exports
└── farmer_crm.py     # All models, services, and query interface
```

## Key Components

### Enums

| Enum | Values | Purpose |
|------|--------|---------|
| `FarmerStatus` | lead, registered, active, premium, churned | Farmer lifecycle state |
| `DealStage` | prospecting, qualification, negotiation, contracted, delivered, paid, closed_lost | Harvest deal pipeline |
| `InteractionType` | advisory, support, sales, training, inspection | Interaction category |

### Data Models

| Model | Description |
|-------|-------------|
| `Farmer` | Core entity: name (bilingual), phone, location, farm details, engagement metrics, lifetime value |
| `HarvestDeal` | Opportunity: crop type, expected quantity/price, pipeline stage, win probability |
| `Interaction` | Activity log: type, subject (bilingual), advisor, outcome, follow-up flag |
| `SupplyContract` | Formal contract: terms, delivery dates, quality requirements, payment schedule |
| `Payment` | Payment record: amount, currency, type (bank/cash/mobile), status |

### Services

**`FarmerCRMService`** - Main service for farmer relationship management:
- `create_farmer()` - Register new farmer with auto-generated ID (`FRM-XXXXXXXX`)
- `update_farmer_status()` - Lifecycle state transitions
- `create_deal()` - Open harvest deal in pipeline
- `advance_deal_stage()` - Move deal through stages with automatic probability update
- `log_interaction()` - Record advisory, support, or training interactions
- `get_pipeline_summary()` - Dashboard data: counts and values by stage
- `get_farmer_analytics()` - Per-farmer deal history, interaction counts, engagement score (0-100)

**`FarmerQueryBot`** - Natural language query interface (SQLBot-inspired):
- Processes Arabic and English queries against CRM data
- Supports: farmer counts by status, pipeline summaries, top farmers by value

## Usage Example

```python
from shared.crm import FarmerCRMService, FarmerQueryBot, InteractionType, DealStage

crm = FarmerCRMService(tenant_id="farm_001")

# Register a farmer
farmer = await crm.create_farmer(
    name="Ahmed Al-Rashid",
    name_ar="أحمد الراشد",
    phone="+966501234567",
    governorate="الرياض",
    primary_crops=["wheat", "barley"],
    total_area_ha=50.0,
)

# Open a harvest deal
deal = await crm.create_deal(
    farmer_id=farmer.farmer_id,
    crop_type="wheat",
    expected_quantity=120,   # tons
    expected_price=1850,     # SAR/ton
)

# Advance through pipeline
await crm.advance_deal_stage(deal.deal_id, DealStage.CONTRACTED)

# Log an advisory interaction
await crm.log_interaction(
    farmer_id=farmer.farmer_id,
    type=InteractionType.ADVISORY,
    subject="Nitrogen deficiency treatment",
    subject_ar="علاج نقص النيتروجين",
)

# Natural language query
bot = FarmerQueryBot(crm)
result = await bot.query("كم عدد المزارعين النشطين؟")
# {"count": 42, "answer": "عدد المزارعين (active): 42"}

# Pipeline dashboard
summary = await crm.get_pipeline_summary()
# {"total_deals": 15, "total_value": 2_775_000, "weighted_value": 1_387_500}
```

## Engagement Score

The service computes a 0-100 engagement score per farmer based on:
- Recency of last interaction (up to 30 points)
- Total number of interactions (up to 25 points)
- Active open deals (up to 25 points)
- Profile completeness: email, coordinates, crops, area (up to 20 points)

## Notes

- Storage is currently in-memory (`dict`). In production, replace with asyncpg/PostgreSQL queries.
- `FarmerQueryBot` uses pattern matching. For production, wire it to an LLM via `shared/ai/llm_provider.py`.
- Deal IDs are `DEAL-XXXXXXXX` and interaction IDs are `INT-XXXXXXXX` (8 hex chars, uppercased).
- All bilingual fields follow the pattern `name` (English) / `name_ar` (Arabic).
