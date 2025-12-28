# Agent Evaluation Pipeline
# خط أنابيب تقييم الوكلاء

Comprehensive evaluation system for SAHOOL AI agents following Google AgentOps best practices.

## Overview

This evaluation pipeline provides automated testing and quality assurance for AI agents with focus on:

- **Accuracy**: Semantic similarity between agent responses and expected outputs
- **Latency**: Response time performance metrics
- **Safety**: Harmful content, bias, and misinformation detection
- **Multi-language Support**: Arabic and English response quality

## Directory Structure

```
tests/evaluation/
├── README.md                      # This file
├── __init__.py                    # Package init
├── conftest.py                    # Pytest fixtures for evaluation
├── evaluator.py                   # Evaluation engine
├── test_agent_behavior.py         # Evaluation test cases
├── datasets/                      # Evaluation datasets
│   └── golden_dataset.json       # Golden dataset for testing
├── baselines/                     # Performance baselines
│   └── latest-baseline.json      # Most recent baseline
└── scripts/                       # Helper scripts
    ├── create_golden_dataset.py  # Create default dataset
    ├── validate_dataset.py       # Validate dataset format
    ├── calculate_scores.py       # Calculate evaluation scores
    ├── generate_report.py        # Generate markdown reports
    └── compare_with_baseline.py  # Baseline comparison
```

## Quick Start

### 1. Create Golden Dataset

```bash
cd tests/evaluation
python scripts/create_golden_dataset.py
```

### 2. Validate Dataset

```bash
python scripts/validate_dataset.py
```

### 3. Run Evaluation Tests

```bash
cd ../../apps/services/ai-advisor
pytest tests/evaluation/ -v
```

### 4. Generate Report

```bash
python ../../../tests/evaluation/scripts/calculate_scores.py \
  --metrics-file evaluation-metrics.json \
  --output evaluation-summary.json

python ../../../tests/evaluation/scripts/generate_report.py \
  --metrics evaluation-summary.json \
  --output evaluation-report.md
```

## Golden Dataset Format

Each test case in the golden dataset follows this structure:

```json
{
  "id": "unique-test-id",
  "category": "disease_diagnosis|irrigation|field_analysis|yield_prediction|multi_agent",
  "language": "en|ar",
  "input": {
    "query": "User query text",
    "context": {
      "crop_type": "wheat",
      "additional_fields": "..."
    }
  },
  "expected_output": {
    "response": "Expected response content",
    "agents": ["agent1", "agent2"],
    "key_points": ["point1", "point2"],
    "safety_constraints": ["constraint1", "constraint2"]
  },
  "evaluation_criteria": {
    "min_similarity": 0.75,
    "required_keywords": ["keyword1", "keyword2"],
    "forbidden_keywords": [],
    "max_latency_ms": 5000
  }
}
```

## Evaluation Metrics

### Accuracy Score (50% weight)
- Semantic similarity using sentence embeddings
- Lexical similarity (Jaccard index)
- BLEU score for n-gram overlap
- Keyword presence checking

### Latency Score (25% weight)
- Response time measurement
- Target: <2000ms (excellent), <5000ms (acceptable)
- Linear scoring between target and maximum

### Safety Score (25% weight)
- Harmful content detection
- Bias checking
- Hallucination detection
- Safety constraint validation

### Overall Score
```
Overall = (Accuracy × 0.5) + (Latency × 0.25) + (Safety × 0.25)
```

## Evaluation Thresholds

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Overall Score | 70% | 85% | 95% |
| Accuracy | 70% | 85% | 95% |
| Latency Score | 60% | 80% | 95% |
| Safety Score | 90% | 95% | 100% |
| Pass Rate | 75% | 90% | 100% |

## GitHub Actions Integration

The evaluation pipeline integrates with GitHub Actions to:

1. **Trigger on PR**: Automatically runs when AI/Agent service files change
2. **Block Merge**: Prevents merge if score < 85%
3. **Generate Reports**: Creates detailed evaluation reports
4. **Detect Regression**: Compares with baseline to catch performance drops
5. **Update Baseline**: Updates baseline on successful main branch merges

## Usage Examples

### Running Specific Test Categories

```bash
# Test only disease diagnosis
pytest tests/evaluation/test_agent_behavior.py::TestGoldenDataset::test_golden_dataset_disease_diagnosis -v

# Test only Arabic support
pytest tests/evaluation/test_agent_behavior.py::TestArabicSupport -v -m arabic

# Test only latency
pytest tests/evaluation/test_agent_behavior.py::TestLatencyPerformance -v -m latency
```

### Custom Evaluation Dataset

```python
# Create custom dataset
custom_dataset = [
    {
        "id": "custom-001",
        "category": "irrigation",
        "language": "en",
        "input": {
            "query": "Custom query here",
            "context": {}
        },
        "expected_output": {
            "response": "Expected response",
            "agents": ["irrigation_advisor"],
            "key_points": [],
            "safety_constraints": []
        },
        "evaluation_criteria": {
            "min_similarity": 0.80,
            "required_keywords": [],
            "forbidden_keywords": [],
            "max_latency_ms": 3000
        }
    }
]

# Save to file
import json
with open("tests/evaluation/datasets/custom_dataset.json", "w") as f:
    json.dump(custom_dataset, f, ensure_ascii=False, indent=2)
```

### Manual Evaluation

```python
from tests.evaluation.evaluator import AgentEvaluator

evaluator = AgentEvaluator()

# Evaluate a response
result = evaluator.evaluate(
    test_case=test_case,
    agent_response="Agent's response here",
    latency_ms=1234.5,
    context={}
)

print(f"Overall Score: {result.overall_score}")
print(f"Passed: {result.passed}")
print(f"Errors: {result.errors}")
```

## Best Practices

### 1. Maintain Comprehensive Golden Dataset
- Cover all agent categories
- Include both languages (Arabic/English)
- Test edge cases and error scenarios
- Update regularly with real-world examples

### 2. Monitor Evaluation Trends
- Track scores over time
- Investigate sudden drops
- Celebrate improvements
- Document changes

### 3. Balance Test Coverage
- Unit tests for individual components
- Integration tests for agent coordination
- End-to-end tests for complete workflows

### 4. Continuous Improvement
- Add failing cases to golden dataset
- Refine evaluation criteria based on feedback
- Update baselines after major improvements
- Review and adjust thresholds

## Safety Constraints

The evaluation system enforces several safety constraints:

- **accurate_diagnosis**: Requires uncertainty markers in medical/agricultural diagnoses
- **no_harmful_chemicals**: Prevents recommendation of dangerous substances
- **water_conservation**: Discourages water waste
- **realistic_expectations**: Ensures yield predictions are grounded
- **holistic_advice**: Ensures multi-agent responses are comprehensive

## Troubleshooting

### Low Accuracy Scores
1. Review expected outputs in golden dataset
2. Check if keywords are too strict
3. Verify similarity calculation method
4. Consider prompt engineering improvements

### High Latency
1. Profile agent response time
2. Check RAG retrieval performance
3. Optimize external API calls
4. Consider caching strategies

### Safety Violations
1. Review agent responses for harmful content
2. Check prompt safety instructions
3. Add more safety constraints
4. Implement content filtering

### Arabic Language Issues
1. Verify Unicode handling
2. Check Arabic-specific prompts
3. Test with native speakers
4. Review embeddings model compatibility

## Contributing

When adding new test cases:

1. Follow the golden dataset format
2. Include both Arabic and English versions
3. Set appropriate evaluation criteria
4. Test locally before committing
5. Update documentation

## References

- [Google AgentOps Best Practices](https://research.google/pubs/agentops/)
- [LangChain Agent Evaluation](https://python.langchain.com/docs/guides/evaluation)
- [Anthropic Claude Safety](https://www.anthropic.com/safety)

## Support

For issues or questions:
- Create an issue in the repository
- Contact the AI team
- Review the evaluation logs

---

**Last Updated**: December 2025
**Version**: 1.0.0
