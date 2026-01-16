# SAHOOL Skills CLI - Testing & Development Guide

دليل اختبار مهارات سهول - Skills CLI Testing Guide

A comprehensive command-line interface for testing and evaluating agricultural AI skills in the SAHOOL platform. This tool enables developers to test context compression, farm memory management, advisory evaluation, and skill documentation.

## Features

### 1. Context Compression
Reduce token usage while preserving critical agricultural data using multiple compression levels.

- **Light compression**: 80% retention - removes redundant spaces
- **Medium compression**: 50% retention - condenses repetitions
- **Heavy compression**: 25% retention - extracts key terms only

### 2. Farm Memory Management
Store and retrieve agricultural operation history with tenant isolation and bilingual support.

- Store observations, actions, recommendations, weather data
- Retrieve with filtering by field, type, and time
- Support for English and Arabic content
- JSON input/output

### 3. Advisory Quality Evaluation
Evaluate agricultural advisories using LLM-as-Judge methodology with domain-specific rubrics.

- Multi-dimensional scoring (accuracy, relevance, actionability, timeliness, safety)
- Support for irrigation, fertilizer, and pest management advisories
- Weighted scoring system
- Improvement suggestions

### 4. Documentation Generation
Generate and manage skill documentation in multiple formats.

- List available skills
- View detailed skill documentation
- Export to JSON, HTML, or Markdown formats

## Installation

### Prerequisites

- Python 3.8+
- Click library: `pip install click`

### Setup

```bash
# Make executable
chmod +x scripts/skills_cli.py

# Verify installation
python scripts/skills_cli.py --help
```

## Quick Start

### Compress Agricultural Data

```bash
# Compress English text
python scripts/skills_cli.py compress \
  --text "Your field data here..." \
  --level medium

# Compress JSON field data
python scripts/skills_cli.py compress \
  --json '{"name": "Field001", "area": 8.5, "crop": "wheat"}' \
  --level heavy

# Arabic text compression
python scripts/skills_cli.py compress \
  --text "بيانات الحقل..." \
  --language ar
```

### Store Memory Entries

```bash
# Simple observation
python scripts/skills_cli.py remember \
  --tenant-id t1 \
  --field-id f1 \
  --type observation \
  --content "Wheat shows yellow tips"

# JSON content
python scripts/skills_cli.py remember \
  --tenant-id t1 \
  --field-id f1 \
  --type action \
  --json '{"action": "irrigation", "volume": "500m3/ha"}'

# Arabic memory
python scripts/skills_cli.py remember \
  --tenant-id t1 \
  --field-id f1 \
  --type observation \
  --content "القمح يظهر أطراف صفراء" \
  --language ar
```

### Retrieve Memory

```bash
# Get all observations for a field
python scripts/skills_cli.py recall \
  --tenant-id t1 \
  --field-id f1 \
  --type observation

# Get recent memories with limit
python scripts/skills_cli.py recall \
  --tenant-id t1 \
  --field-id f1 \
  --limit 10
```

### Evaluate Advisory Quality

```bash
# Evaluate irrigation advice
python scripts/skills_cli.py evaluate \
  --type irrigation \
  --text "Irrigate 500m³/ha tomorrow morning"

# Evaluate with context
python scripts/skills_cli.py evaluate \
  --type pest \
  --text "Spray imidacloprid for aphid control" \
  --context '{"threshold":"25/tiller","current":"12/tiller"}'

# Save to file
python scripts/skills_cli.py evaluate \
  --type fertilizer \
  --text "Apply urea 46kg/ha" \
  --output evaluation.json
```

### Generate Documentation

```bash
# List skills
python scripts/skills_cli.py generate-doc --list

# Show skill details
python scripts/skills_cli.py generate-doc --skill compression

# Export documentation
python scripts/skills_cli.py generate-doc \
  --skill all \
  --format markdown \
  --output skills.md
```

## Detailed Usage Guide

### Compress Command

#### Options

```
--text TEXT              Text to compress
--json JSON              JSON field data to compress
--level {light|medium|heavy}  Compression level (default: medium)
--language {ar|en|auto}  Language hint for tokenization (default: auto)
--output FILE            Save output to JSON file
```

#### Examples

**Compress long field report with heavy compression:**
```bash
python scripts/skills_cli.py compress \
  --text "Field 003 covers 8.5 hectares with wheat variety Sakha-95. \
The field uses center pivot irrigation. Soil type is clay loam with pH 7.2. \
Current NDVI reading is 0.72 indicating healthy vegetation. \
The crop was planted on November 15, 2024 and is at tillering stage." \
  --level heavy
```

**Output:**
```
Compression Results
────────────────────────────────────────────────────────────
Original tokens:    89
Compressed tokens:  22
Tokens saved:       67 (75.3%)
Compression ratio:  0.25x
```

**Compress structured field data:**
```bash
python scripts/skills_cli.py compress \
  --json '{
    "field_id": "F003",
    "name": "North Wheat Field",
    "area": 8.5,
    "crop": "wheat",
    "variety": "Sakha-95",
    "ndvi": 0.72,
    "soil_type": "clay_loam",
    "irrigation_type": "center_pivot",
    "status": "healthy"
  }' \
  --level light \
  --output compressed_field.json
```

### Remember Command

#### Options

```
--tenant-id TEXT          Tenant identifier (required)
--field-id TEXT           Field identifier (optional)
--type {observation|action|recommendation|...}  Memory type
--content TEXT            Text content
--json JSON               JSON content
--language {ar|en}        Content language (default: en)
--output FILE             Save to JSON file
```

#### Memory Types

- **conversation**: Chat/interaction history
- **field_state**: Field status snapshots
- **recommendation**: AI recommendations
- **observation**: Field observations
- **weather**: Weather data
- **action**: User actions
- **system**: System events

#### Examples

**Store field observation with metadata:**
```bash
python scripts/skills_cli.py remember \
  --tenant-id tenant_001 \
  --field-id field_003 \
  --type observation \
  --json '{
    "crop_stage": "tillering",
    "issue": "yellowing",
    "location": "eastern_corner",
    "severity": "moderate"
  }'
```

**Store Arabic recommendation:**
```bash
python scripts/skills_cli.py remember \
  --tenant-id tenant_001 \
  --field-id field_003 \
  --type recommendation \
  --content "تطبيق اليوريا بمعدل 46 كغ/هكتار في الصباح" \
  --language ar \
  --output recommendation.json
```

### Recall Command

#### Options

```
--tenant-id TEXT          Tenant identifier (required)
--field-id TEXT           Filter by field ID
--type TEXT               Filter by memory type
--query TEXT              Text query for matching
--limit INT               Maximum entries (default: 20)
--output FILE             Save to JSON file
```

#### Examples

**Recall field history for decision-making:**
```bash
python scripts/skills_cli.py recall \
  --tenant-id tenant_001 \
  --field-id field_003 \
  --limit 10 \
  --output field_history.json
```

**Retrieve specific memory types:**
```bash
python scripts/skills_cli.py recall \
  --tenant-id tenant_001 \
  --field-id field_003 \
  --type action \
  --limit 5
```

### Evaluate Command

#### Options

```
--type {irrigation|fertilizer|pest|general}  Advisory type
--text TEXT               Advisory text to evaluate (required)
--context JSON            Field conditions context
--output FILE             Save evaluation to JSON file
```

#### Evaluation Dimensions

1. **Accuracy** (30% weight): Technical correctness
2. **Relevance** (25% weight): Applicability to situation
3. **Actionability** (20% weight): Clarity and feasibility
4. **Timeliness** (15% weight): Timing appropriateness
5. **Safety** (10% weight): Risk awareness

#### Scoring Scale

- **5 (Excellent)**: Expert-level advice, comprehensive
- **4 (Good)**: Sound advice, minor gaps
- **3 (Adequate)**: Acceptable but incomplete
- **2 (Poor)**: Significant errors or omissions
- **1 (Failing)**: Incorrect or potentially harmful

#### Examples

**Evaluate comprehensive irrigation advisory:**
```bash
python scripts/skills_cli.py evaluate \
  --type irrigation \
  --text "Soil moisture is 38%, below the 40% threshold for wheat at tillering stage. \
Given the 5-day dry forecast and ET of 5.8mm/day, irrigate immediately. \
Apply 500 m³/ha using center pivot. Optimal window: 6-8 AM tomorrow to minimize evaporation. \
Target soil moisture: 55%. Monitor drainage to prevent waterlogging. \
Re-check in 7 days." \
  --context '{
    "field": "F003",
    "crop": "wheat",
    "stage": "tillering",
    "soil_moisture": 38,
    "threshold": 40,
    "et": 5.8,
    "equipment": "center_pivot"
  }' \
  --output irrigation_eval.json
```

**Evaluate pest management with IPM considerations:**
```bash
python scripts/skills_cli.py evaluate \
  --type pest \
  --text "Aphid population at 12/tiller is below economic threshold. \
Beneficial insects present. Monitor daily - scout 10 tillers at 5 locations. \
Spray ONLY if exceeds 25 aphids/tiller. If needed: Imidacloprid 100ml/ha, \
early morning, avoid rain 6h. PHI: 21 days, REI: 12 hours." \
  --context '{
    "current_population": 12,
    "threshold": 25,
    "beneficial_insects": "ladybugs_present",
    "neighboring_fields": "moderate_infestation"
  }'
```

### Generate-Doc Command

#### Options

```
--list                    List all available skills
--skill {compression|memory|evaluation|all}  Skill to document
--format {text|json|html|markdown}  Output format (default: text)
--output FILE             Save documentation to file
```

#### Examples

**Generate all documentation as Markdown:**
```bash
python scripts/skills_cli.py generate-doc \
  --skill all \
  --format markdown \
  --output skills_documentation.md
```

**Export compression skill as JSON:**
```bash
python scripts/skills_cli.py generate-doc \
  --skill compression \
  --format json \
  --output compression_skill.json
```

## JSON Input/Output Format

### Compression Output

```json
{
  "original_text": "Full original text...",
  "compressed_text": "Compressed text...",
  "original_tokens": 89,
  "compressed_tokens": 22,
  "compression_ratio": 0.2472,
  "tokens_saved": 67,
  "savings_percentage": 75.28
}
```

### Memory Entry Format

```json
{
  "id": "uuid",
  "tenant_id": "tenant_001",
  "field_id": "field_003",
  "memory_type": "observation",
  "content": "Text or structured data",
  "timestamp": "2025-01-13T10:30:00",
  "language": "en"
}
```

### Evaluation Output

```json
{
  "advisory_id": "ADV-20250113103000",
  "advisory_type": "irrigation",
  "scores": {
    "accuracy": 4.0,
    "relevance": 4.5,
    "actionability": 4.0,
    "timeliness": 4.0,
    "safety": 3.5
  },
  "overall_score": 4.1,
  "grade": "Good",
  "strengths": [
    "Specific water volume recommendation",
    "Considers weather forecast",
    "Equipment-specific guidance"
  ],
  "weaknesses": [
    "Missing disease risk warning"
  ]
}
```

## Advanced Usage Patterns

### Workflow: Full Advisory Cycle

```bash
# Step 1: Store field observation
python scripts/skills_cli.py remember \
  --tenant-id farm_001 \
  --field-id field_003 \
  --type observation \
  --content "Wheat yellowing detected in eastern corner"

# Step 2: Compress for context window
python scripts/skills_cli.py compress \
  --json '{"field":"F003","issue":"yellowing","location":"east"}' \
  --level light

# Step 3: Evaluate AI-generated recommendation
python scripts/skills_cli.py evaluate \
  --type fertilizer \
  --text "Apply 46 kg/ha urea early morning with dew present" \
  --output advisory_quality.json

# Step 4: Store action taken
python scripts/skills_cli.py remember \
  --tenant-id farm_001 \
  --field-id field_003 \
  --type action \
  --json '{"action":"applied_urea","rate":"46kg/ha","time":"2025-01-14T07:30Z"}'

# Step 5: Retrieve complete history
python scripts/skills_cli.py recall \
  --tenant-id farm_001 \
  --field-id field_003 \
  --output field_complete_history.json
```

### Batch Evaluation

```bash
# Create advisories file
cat > advisories.txt << EOF
irrigation|Irrigate 500m³/ha tomorrow morning due to low soil moisture
fertilizer|Apply urea 46kg/ha in early morning
pest|Monitor aphids daily, spray if exceeds 25/tiller
EOF

# Evaluate each
while IFS='|' read type text; do
  python scripts/skills_cli.py evaluate \
    --type "$type" \
    --text "$text" \
    --output "eval_${type}.json"
done < advisories.txt
```

### Multi-language Farm Memory

```bash
# Store observations in different languages
python scripts/skills_cli.py remember \
  --tenant-id farm_001 \
  --field-id field_003 \
  --type observation \
  --content "Wheat at tillering stage showing healthy growth" \
  --language en

python scripts/skills_cli.py remember \
  --tenant-id farm_001 \
  --field-id field_003 \
  --type observation \
  --content "القمح في مرحلة التفريع يظهر نمواً صحياً" \
  --language ar

# Recall all (mixed language)
python scripts/skills_cli.py recall \
  --tenant-id farm_001 \
  --field-id field_003
```

## Error Handling

The CLI provides helpful error messages:

```bash
# Invalid JSON
$ python scripts/skills_cli.py compress --json 'invalid json'
Error: Invalid JSON - Expecting value: line 1 column 1 (char 0)

# Missing required parameter
$ python scripts/skills_cli.py remember --tenant-id t1
Error: Provide either --content or --json

# Invalid choice
$ python scripts/skills_cli.py evaluate --type invalid --text "test"
Error: Invalid value for '--type'
```

## Development Tips

### Adding New Skills

1. Extend the evaluation logic in `evaluate_advisory()`
2. Add new memory types to `MemoryType` enum
3. Update documentation in `generate_doc()` command

### Testing Commands

```bash
# Test compress with different levels
for level in light medium heavy; do
  python scripts/skills_cli.py compress \
    --text "Test text for compression..." \
    --level $level
done

# Test memory with different types
for type in observation action recommendation; do
  python scripts/skills_cli.py remember \
    --tenant-id test \
    --field-id f1 \
    --type $type \
    --content "Test content"
done
```

### Debugging

Enable verbose logging:

```bash
# Set logging level
export PYTHONVERBOSE=1
python scripts/skills_cli.py compress --text "test" 2>&1 | head -50
```

## Integration with Other Tools

### With jq (JSON processing)

```bash
# Extract compression ratio
python scripts/skills_cli.py compress --text "..." --json | jq '.compression_ratio'

# Filter memory entries
python scripts/skills_cli.py recall --tenant-id t1 --json | \
  jq '.entries[] | select(.memory_type == "observation")'
```

### With curl (API integration)

```bash
# Compress before sending to API
COMPRESSED=$(python scripts/skills_cli.py compress --json '{"data":"..."}' --json | jq .compressed_text)
curl -X POST https://api/endpoint -d "{\"data\":$COMPRESSED}"
```

### Pipeline Usage

```bash
# Combine compression and evaluation
python scripts/skills_cli.py compress --text "advisory text..." | \
  jq .compressed_text | \
  xargs -I {} python scripts/skills_cli.py evaluate --type general --text "{}"
```

## Performance Considerations

- **Token Estimation**: Uses approximate character-to-token ratios
- **Compression**: Suitable for real-time use
- **Memory**: Scales with number of stored entries
- **Evaluation**: Quick scoring based on text analysis

## Troubleshooting

### "No module named 'click'"
```bash
pip install click
```

### Unicode/Arabic Text Issues
```bash
# Ensure UTF-8 encoding
export PYTHONIOENCODING=utf-8
python scripts/skills_cli.py remember --content "نص عربي"
```

### JSON Parsing Errors
```bash
# Validate JSON before passing
echo '{"data":"value"}' | python -m json.tool

# Use single quotes for outer shell, double quotes for JSON
python scripts/skills_cli.py compress --json '{"field":"F003"}'
```

## Examples Reference

Show all examples:
```bash
python scripts/skills_cli.py examples
```

## Version & Help

```bash
python scripts/skills_cli.py --version
python scripts/skills_cli.py --help
python scripts/skills_cli.py <command> --help
```

## Contributing

To improve the CLI:

1. Test all commands before committing
2. Add examples for new features
3. Update documentation
4. Ensure bilingual (Arabic/English) support
5. Follow the existing code style

## License

Proprietary - SAHOOL Platform

---

**For more information:**
- See `/home/user/sahool-unified-v15-idp/.claude/skills/` for skill definitions
- Check `CLAUDE.md` for platform guidelines
- Review test examples in this documentation
