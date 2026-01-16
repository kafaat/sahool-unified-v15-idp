# LLM-as-Judge Evaluation Skill

## Description

This skill enables systematic evaluation of agricultural AI advisory quality using LLM-as-Judge methodology. It provides structured rubrics for assessing crop recommendations, irrigation advice, pest management guidance, and farmer communication in SAHOOL platform. Supports bilingual Arabic/English evaluation with domain-specific agricultural criteria.

## Instructions

### Evaluation Framework

Use multi-dimensional evaluation with weighted criteria specific to agricultural advisory:

```yaml
evaluation_dimensions:
  accuracy:
    weight: 0.30
    description: Technical correctness of agricultural advice
  relevance:
    weight: 0.25
    description: Applicability to specific field/crop/farmer context
  actionability:
    weight: 0.20
    description: Clarity and feasibility of recommended actions
  timeliness:
    weight: 0.15
    description: Appropriateness of timing recommendations
  safety:
    weight: 0.10
    description: Risk awareness and safety considerations
```

### Scoring Scale

Use a 5-point scale with clear agricultural anchors:

| Score | Label | Description (EN) | الوصف (AR) |
|-------|-------|------------------|------------|
| 5 | Excellent | Expert-level advice, comprehensive | نصيحة على مستوى الخبراء |
| 4 | Good | Sound advice, minor gaps | نصيحة سليمة، فجوات طفيفة |
| 3 | Adequate | Acceptable but incomplete | مقبول لكن غير مكتمل |
| 2 | Poor | Significant errors or omissions | أخطاء أو إغفالات كبيرة |
| 1 | Failing | Incorrect or potentially harmful | خاطئ أو ضار محتملاً |

### Evaluation Rubrics by Advisory Type

#### Irrigation Advisory Rubric

```yaml
irrigation_evaluation:
  accuracy:
    5: Correct water volume, timing, method; accounts for ET, soil, crop stage
    4: Correct recommendation with minor calculation variance (<10%)
    3: Generally correct but missing key factor (e.g., soil type)
    2: Significant error in volume or timing
    1: Recommendation would cause water stress or waterlogging

  relevance:
    5: Fully customized to field sensors, crop stage, weather forecast
    4: Considers most relevant factors
    3: Generic recommendation partially applicable
    2: Mismatched to current conditions
    1: Irrelevant to field/crop situation

  actionability:
    5: Specific volume, timing, duration; equipment instructions
    4: Clear recommendation, minor details missing
    3: Understandable but vague on specifics
    2: Confusing or contradictory instructions
    1: Impossible to execute as written

  timeliness:
    5: Optimal window specified with flexibility range
    4: Good timing with acceptable range
    3: Timing correct but no urgency indication
    2: Timing off by >24 hours
    1: Critically late or premature recommendation

  safety:
    5: Addresses over-irrigation risks, disease, runoff
    4: Notes major safety considerations
    3: Implicit safety awareness
    2: Ignores obvious risks
    1: Recommendation poses plant/environmental risk
```

#### Fertilizer Advisory Rubric

```yaml
fertilizer_evaluation:
  accuracy:
    5: Correct nutrient, rate, form based on soil test and crop needs
    4: Sound recommendation, minor rate adjustment needed
    3: Correct nutrient but suboptimal rate or timing
    2: Wrong nutrient priority or significant rate error
    1: Recommendation would cause toxicity or deficiency

  relevance:
    5: Matches soil test, crop stage, variety requirements, farmer constraints
    4: Considers most agronomic factors
    3: Generic recommendation for crop type
    2: Doesn't match current nutrient status
    1: Contradicts soil test or crop needs

  actionability:
    5: Specific product, rate, method, timing; cost estimate included
    4: Clear instructions, minor details missing
    3: General guidance, farmer must determine specifics
    2: Vague or incomplete instructions
    1: Cannot be executed without clarification

  timeliness:
    5: Optimal growth stage, weather window, soil conditions specified
    4: Good timing recommendation
    3: Acceptable timing without weather consideration
    2: Suboptimal timing (e.g., before heavy rain)
    1: Timing would result in loss or crop damage

  safety:
    5: Addresses application safety, environmental impact, PHI if applicable
    4: Notes major safety considerations
    3: Basic safety awareness
    2: Ignores application hazards
    1: Unsafe recommendation (e.g., near water source)
```

#### Pest Management Advisory Rubric

```yaml
pest_evaluation:
  accuracy:
    5: Correct pest ID, threshold assessment, effective control option
    4: Accurate recommendation, alternative options available
    3: Correct approach but missing IPM considerations
    2: Misidentification or wrong control method
    1: Recommendation ineffective or would worsen problem

  relevance:
    5: Considers pest pressure, crop stage, beneficial insects, resistance
    4: Addresses main factors
    3: Generic pest control for identified pest
    2: Doesn't account for local conditions
    1: Inappropriate for current situation

  actionability:
    5: Specific product, rate, timing, PHI, re-entry; scouting follow-up
    4: Clear recommendation with application details
    3: General control method, specifics needed
    2: Vague instructions
    1: Cannot be safely executed

  timeliness:
    5: Threshold-based timing, weather window, re-application schedule
    4: Good timing with conditions
    3: Acceptable timing
    2: Premature or late intervention
    1: Critical timing error (past effective window)

  safety:
    5: PPE requirements, PHI, beneficial insect protection, drift prevention
    4: Covers major safety aspects
    3: Basic safety notes
    2: Inadequate safety guidance
    1: Unsafe recommendation or missing critical warnings
```

### Evaluation Process

1. **Context Review**: Understand field conditions, farmer query, available data
2. **Response Analysis**: Parse advisory into actionable components
3. **Dimension Scoring**: Score each dimension against rubric
4. **Weighted Calculation**: Apply weights to compute overall score
5. **Justification**: Provide evidence-based rationale for each score
6. **Improvement Suggestions**: Identify specific enhancements

### Output Format

```yaml
evaluation_result:
  advisory_id: ADV-2025-XXX
  advisory_type: irrigation | fertilizer | pest | general
  evaluator: LLM-as-Judge
  timestamp: ISO-8601

  scores:
    accuracy:
      score: X/5
      rationale: "..."
      evidence: ["..."]
    relevance:
      score: X/5
      rationale: "..."
      evidence: ["..."]
    actionability:
      score: X/5
      rationale: "..."
      evidence: ["..."]
    timeliness:
      score: X/5
      rationale: "..."
      evidence: ["..."]
    safety:
      score: X/5
      rationale: "..."
      evidence: ["..."]

  overall_score: X.XX/5.00
  grade: Excellent | Good | Adequate | Poor | Failing

  strengths: ["..."]
  weaknesses: ["..."]
  improvements: ["..."]

  arabic_summary: "..."
```

### Comparison Evaluation

When comparing two advisory responses:

```yaml
comparison_evaluation:
  advisory_a:
    source: baseline_model
    overall_score: X.XX
  advisory_b:
    source: improved_model
    overall_score: X.XX
  winner: A | B | TIE
  margin: significant | marginal | negligible
  key_differentiators: ["..."]
```

### Domain-Specific Checks

#### Crop-Specific Validation
- Wheat: Check Zadoks growth stage alignment
- Date Palm: Verify seasonal timing (pollination, harvest)
- Vegetables: Confirm PHI (pre-harvest interval) compliance
- All: Validate regional/climate appropriateness

#### Safety Critical Checks
- Pesticide recommendations must include:
  - Product registration status
  - PHI (pre-harvest interval)
  - REI (restricted entry interval)
  - PPE requirements
  - Drift and runoff warnings
- Fertilizer recommendations must consider:
  - Soil test results
  - Groundwater proximity
  - Application timing vs. rainfall
- Irrigation must account for:
  - Salinity management
  - Disease risk (over-irrigation)
  - Water quality

## Examples

### Example 1: Evaluate Irrigation Advisory

**Advisory Under Evaluation:**
```
Based on current soil moisture of 38% and no rain forecast for 5 days,
irrigate Field 003 with 500 m³/ha using the center pivot system.
Schedule irrigation for early morning tomorrow.
```

**Context:**
- Field: FIELD-003, 8.5 ha wheat at tillering stage
- Soil moisture: 38% (threshold: 40%)
- ET₀: 5.8 mm/day
- Weather: Clear, no rain 5 days
- Equipment: Center pivot irrigation

**Evaluation:**
```yaml
evaluation_result:
  advisory_id: ADV-2025-010
  advisory_type: irrigation
  evaluator: LLM-as-Judge
  timestamp: 2025-01-13T14:00:00Z

  scores:
    accuracy:
      score: 4/5
      rationale: |
        Water volume calculation is reasonable for bringing soil to field
        capacity. However, did not show ET-based calculation or account
        for root zone depth at tillering stage.
      evidence:
        - "500 m³/ha is within acceptable range for wheat at tillering"
        - "Should specify target moisture level (e.g., 55%)"
        - "Missing: crop coefficient (Kc) consideration"

    relevance:
      score: 5/5
      rationale: |
        Directly addresses the field-specific situation with correct
        equipment reference and current moisture status.
      evidence:
        - "References correct field ID and equipment"
        - "Accounts for 5-day dry forecast"
        - "Appropriate for crop stage"

    actionability:
      score: 3/5
      rationale: |
        Provides volume and timing but lacks specific operational details
        for pivot system (run time, speed setting).
      evidence:
        - "Volume specified: 500 m³/ha"
        - "Timing specified: early morning"
        - "Missing: pivot run time calculation"
        - "Missing: expected irrigation duration"

    timeliness:
      score: 4/5
      rationale: |
        Recommends tomorrow morning which is appropriate given the 38%
        moisture, but should specify optimal window hours.
      evidence:
        - "Early morning timing reduces evaporation"
        - "Should specify: 5-8 AM optimal window"
        - "Could note: adjust if wind >15 km/h"

    safety:
      score: 3/5
      rationale: |
        Does not address over-irrigation risks or disease potential in
        wheat at tillering stage.
      evidence:
        - "Missing: foliar disease warning (wet canopy)"
        - "Should note: avoid evening irrigation"
        - "Could mention: drainage check"

  overall_score: 3.85/5.00
  grade: Good

  strengths:
    - "Correct threshold-based trigger for irrigation"
    - "Appropriate volume recommendation"
    - "Weather-informed decision"

  weaknesses:
    - "Lacks operational specifics for pivot system"
    - "No ET-based calculation shown"
    - "Missing safety considerations for disease"

  improvements:
    - "Add pivot run time: ~4 hours at 50% speed"
    - "Include target soil moisture: 55%"
    - "Add note: irrigate early AM to allow canopy drying"
    - "Specify next irrigation: re-check in 5-7 days"

  arabic_summary: |
    التقييم: جيد (3.85/5)
    النقاط القوية: توقيت صحيح، كمية مناسبة
    نقاط التحسين: إضافة تفاصيل تشغيل المحور، تحذيرات الأمراض
```

### Example 2: Evaluate Pest Management Advisory

**Advisory Under Evaluation:**
```
Aphid infestation detected in Field 003. Apply Imidacloprid 20% at
100 ml/ha immediately. Re-scout after 7 days.

تم اكتشاف إصابة بالمن في الحقل 003. قم برش إيميداكلوبريد 20% بمعدل
100 مل/هكتار فوراً. أعد الفحص بعد 7 أيام.
```

**Context:**
- Field: FIELD-003, wheat at tillering
- Pest: Aphids, 12 per tiller (threshold: 25)
- Beneficial insects: Ladybugs observed
- Neighboring fields: Moderate infestation reported

**Evaluation:**
```yaml
evaluation_result:
  advisory_id: ADV-2025-011
  advisory_type: pest
  evaluator: LLM-as-Judge
  timestamp: 2025-01-13T15:00:00Z

  scores:
    accuracy:
      score: 2/5
      rationale: |
        Recommends immediate spray when population (12/tiller) is below
        economic threshold (25/tiller). This is premature treatment.
      evidence:
        - "Current: 12 aphids/tiller"
        - "Threshold: 25 aphids/tiller"
        - "Treatment should wait until threshold exceeded"
        - "Product choice (Imidacloprid) is effective but premature"

    relevance:
      score: 2/5
      rationale: |
        Ignores presence of beneficial insects (ladybugs) which provide
        natural control. Does not consider IPM approach.
      evidence:
        - "Ladybugs observed - natural control active"
        - "Missing: IPM consideration"
        - "Should recommend monitoring over immediate spray"

    actionability:
      score: 4/5
      rationale: |
        Clear product, rate, and follow-up schedule. Missing application
        details but executable instruction.
      evidence:
        - "Product: Imidacloprid 20%"
        - "Rate: 100 ml/ha"
        - "Follow-up: 7-day re-scout"
        - "Missing: application timing, PPE"

    timeliness:
      score: 2/5
      rationale: |
        "Immediately" is premature given below-threshold population.
        Should recommend threshold monitoring first.
      evidence:
        - "Immediate spray not justified at current levels"
        - "Should: monitor daily, spray if >25/tiller"
        - "Neighboring field pressure noted but not imminent"

    safety:
      score: 2/5
      rationale: |
        Missing critical safety information for systemic insecticide.
      evidence:
        - "Missing: PHI (pre-harvest interval)"
        - "Missing: REI (re-entry interval)"
        - "Missing: PPE requirements"
        - "Missing: pollinator protection (if flowering nearby)"
        - "Missing: beneficial insect impact warning"

  overall_score: 2.40/5.00
  grade: Poor

  strengths:
    - "Correct product selection for aphid control"
    - "Appropriate rate recommendation"
    - "Bilingual communication"

  weaknesses:
    - "Premature spray recommendation (below threshold)"
    - "Ignores beneficial insects providing natural control"
    - "Missing IPM approach"
    - "No safety information provided"

  improvements:
    - "Change to: Monitor daily, spray only if >25 aphids/tiller"
    - "Add: Beneficial insects present, may provide natural control"
    - "Include IPM: Consider spot treatment if localized"
    - "Add safety: PHI 21 days, REI 12 hours, wear gloves/goggles"
    - "Note: Avoid spraying if rain expected within 6 hours"

  corrected_advisory: |
    Aphid population at 12/tiller is below treatment threshold (25/tiller).
    Beneficial insects (ladybugs) observed providing natural control.

    RECOMMENDATION:
    1. Monitor daily - check 10 tillers at 5 locations
    2. Spray ONLY if population exceeds 25 aphids/tiller
    3. If spray needed: Imidacloprid 20% at 100 ml/ha
       - Apply early morning, avoid rain within 6h
       - PHI: 21 days | REI: 12 hours
       - PPE: Gloves, eye protection
    4. Re-evaluate in 3 days regardless

    عدد المن (12/فرع) أقل من عتبة العلاج (25/فرع).
    الحشرات النافعة موجودة وتوفر مكافحة طبيعية.
    راقب يومياً، رش فقط إذا تجاوز العدد 25/فرع.

  arabic_summary: |
    التقييم: ضعيف (2.40/5)
    المشكلة الرئيسية: توصية رش مبكرة قبل الوصول للعتبة الاقتصادية
    يجب: المراقبة اليومية، الرش فقط عند تجاوز 25 حشرة/فرع
```

### Example 3: Compare Two Advisory Responses

**Query:** Farmer asks about yellowing wheat leaves in Field 003

**Response A (Baseline):**
```
The yellowing indicates nitrogen deficiency. Apply 46 kg/ha of urea.
```

**Response B (Improved):**
```
Yellowing in the eastern corner of Field 003 suggests nitrogen deficiency,
confirmed by your soil test showing 18 ppm N (target: 25 ppm).

RECOMMENDATION:
- Apply urea (46% N) at 46 kg/ha as top dressing
- Timing: Early morning when dew is present for better absorption
- Method: Broadcast evenly, avoid application before rain
- Expected recovery: 7-10 days for visible greening
- Cost estimate: ~100 SAR/ha

If yellowing persists after 14 days, request follow-up soil test.

يشير الاصفرار في الزاوية الشرقية إلى نقص النيتروجين.
التوصية: يوريا 46 كغ/هكتار صباحاً مع وجود الندى.
```

**Comparison Evaluation:**
```yaml
comparison_evaluation:
  advisory_a:
    source: baseline_model
    scores:
      accuracy: 4/5
      relevance: 2/5
      actionability: 2/5
      timeliness: 1/5
      safety: 1/5
    overall_score: 2.15/5.00

  advisory_b:
    source: improved_model
    scores:
      accuracy: 5/5
      relevance: 5/5
      actionability: 5/5
      timeliness: 4/5
      safety: 4/5
    overall_score: 4.70/5.00

  winner: B
  margin: significant
  score_difference: +2.55

  key_differentiators:
    - "Response B references soil test data (18 ppm)"
    - "Response B provides application method and timing"
    - "Response B includes cost estimate"
    - "Response B has follow-up plan"
    - "Response B is bilingual"
    - "Response A is generic, lacks context"

  dimension_comparison:
    accuracy:
      winner: B
      reason: "B cites specific soil test values"
    relevance:
      winner: B
      reason: "B references specific field location (eastern corner)"
    actionability:
      winner: B
      reason: "B provides complete application instructions"
    timeliness:
      winner: B
      reason: "B specifies timing (early morning with dew)"
    safety:
      winner: B
      reason: "B notes weather consideration (avoid pre-rain)"

  improvement_for_A:
    - "Reference soil test results"
    - "Add application method and timing"
    - "Include expected outcome and timeline"
    - "Provide follow-up instructions"
    - "Add bilingual support"

  arabic_summary: |
    الفائز: الاستجابة ب (4.70 مقابل 2.15)
    الفرق: كبير (+2.55 نقطة)
    السبب: الاستجابة ب تقدم تفاصيل تطبيق كاملة ومرجعية لفحص التربة
```

### Example 4: Batch Evaluation Summary

**Evaluate 10 advisories and generate summary report:**

```yaml
batch_evaluation_summary:
  evaluation_period: 2025-01-01 to 2025-01-13
  total_advisories: 10

  score_distribution:
    excellent (4.5-5.0): 1 (10%)
    good (3.5-4.49): 4 (40%)
    adequate (2.5-3.49): 3 (30%)
    poor (1.5-2.49): 2 (20%)
    failing (<1.5): 0 (0%)

  average_scores_by_dimension:
    accuracy: 3.8/5.0
    relevance: 4.1/5.0
    actionability: 3.2/5.0
    timeliness: 3.5/5.0
    safety: 2.9/5.0

  overall_average: 3.52/5.00

  by_advisory_type:
    irrigation:
      count: 4
      avg_score: 3.8
      common_issue: "Missing operational specifics"
    fertilizer:
      count: 3
      avg_score: 3.6
      common_issue: "Soil test not referenced"
    pest:
      count: 3
      avg_score: 3.1
      common_issue: "Premature treatment recommendations"

  systemic_issues:
    - issue: "Safety information frequently missing"
      frequency: 7/10
      recommendation: "Add safety checklist to all advisories"
    - issue: "Actionability lacking operational details"
      frequency: 6/10
      recommendation: "Include equipment-specific instructions"
    - issue: "IPM approach underutilized in pest advisories"
      frequency: 3/3
      recommendation: "Enforce threshold checking before spray recommendations"

  top_performing_areas:
    - "Relevance to field conditions (4.1/5)"
    - "Accurate nutrient recommendations"
    - "Bilingual communication"

  improvement_priorities:
    1: "Safety information completeness"
    2: "Actionability with equipment specifics"
    3: "IPM-first approach for pest management"

  arabic_summary: |
    ملخص تقييم 10 استشارات:
    المتوسط العام: 3.52/5 (جيد)
    أقوى جانب: الملاءمة للظروف الحقلية (4.1/5)
    أضعف جانب: معلومات السلامة (2.9/5)
    الأولوية: تحسين معلومات السلامة والتفاصيل التشغيلية
```
