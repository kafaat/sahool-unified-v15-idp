# Agent Evaluation Pipeline Setup Guide

# دليل إعداد خط أنابيب تقييم الوكلاء

Complete setup guide for the SAHOOL Agent Evaluation Pipeline.

## Prerequisites

### Python Dependencies

The evaluation pipeline requires the following Python packages:

```bash
# Core testing
pytest>=8.3.4
pytest-asyncio>=0.24.0
pytest-cov>=4.1.0
pytest-html>=4.1.0
pytest-json-report>=1.5.0

# NLP and similarity
sentence-transformers>=2.2.0
nltk>=3.8.0
scikit-learn>=1.3.0

# Optional: for advanced metrics
sacrebleu>=2.3.0
rouge-score>=0.1.2
```

### Install Dependencies

```bash
cd apps/services/ai-advisor
pip install -r requirements.txt
pip install pytest-cov pytest-html pytest-json-report
pip install scikit-learn nltk sacrebleu rouge-score
```

## Initial Setup

### 1. Create Evaluation Directory Structure

The directory structure is already created. Verify it:

```bash
cd tests/evaluation
tree -L 2
```

Expected structure:

```
tests/evaluation/
├── README.md
├── SETUP.md
├── pytest.ini
├── conftest.py
├── evaluator.py
├── test_agent_behavior.py
├── datasets/
│   └── golden_dataset.json
├── baselines/
│   └── .gitkeep
└── scripts/
    ├── create_golden_dataset.py
    ├── validate_dataset.py
    ├── calculate_scores.py
    ├── generate_report.py
    └── compare_with_baseline.py
```

### 2. Create Golden Dataset

Create the initial golden dataset:

```bash
python scripts/create_golden_dataset.py
```

Output:

```
✅ Created golden dataset with 6 test cases
📁 Saved to: datasets/golden_dataset.json

📊 Dataset Summary:
  Categories: {...}
  Languages: {...}
```

### 3. Validate Dataset

Ensure the dataset is properly formatted:

```bash
python scripts/validate_dataset.py
```

You should see:

```
✅ Validation PASSED
```

### 4. Download NLP Models

Download required NLTK data:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### 5. Configure Environment Variables

Create a `.env` file for testing (if not already present):

```bash
# apps/services/ai-advisor/.env
ANTHROPIC_API_KEY=your_test_api_key
OPENAI_API_KEY=your_test_api_key  # Optional
GOOGLE_API_KEY=your_test_api_key   # Optional

# For evaluation mode
EVALUATION_MODE=true
ENABLE_SAFETY_CHECKS=true
ENABLE_LATENCY_TRACKING=true
```

## Running Evaluations

### Local Evaluation

#### Run All Evaluation Tests

```bash
cd apps/services/ai-advisor
pytest ../../../tests/evaluation/ -v
```

#### Run Specific Test Categories

```bash
# Disease diagnosis tests
pytest ../../../tests/evaluation/test_agent_behavior.py::TestGoldenDataset::test_golden_dataset_disease_diagnosis -v

# Arabic language tests
pytest ../../../tests/evaluation/test_agent_behavior.py::TestArabicSupport -v -m arabic

# Latency tests
pytest ../../../tests/evaluation/test_agent_behavior.py::TestLatencyPerformance -v -m latency

# Safety tests
pytest ../../../tests/evaluation/test_agent_behavior.py::TestSafetyCompliance -v -m safety
```

#### Generate Coverage Report

```bash
pytest ../../../tests/evaluation/ \
  --cov=src \
  --cov-report=html \
  --cov-report=term
```

### CI/CD Evaluation

The GitHub Actions workflow automatically runs on:

- Pull requests to main/develop
- Changes to `apps/services/ai-advisor/**`
- Changes to `tests/evaluation/**`

Manual trigger:

```bash
# Using GitHub CLI
gh workflow run agent-evaluation.yml

# Or through GitHub UI:
# Actions → Agent Evaluation Pipeline → Run workflow
```

## Evaluation Workflow

### 1. Run Tests

```bash
cd apps/services/ai-advisor
pytest ../../../tests/evaluation/ \
  -v \
  --json-report \
  --json-report-file=evaluation-metrics.json
```

### 2. Calculate Scores

```bash
python ../../../tests/evaluation/scripts/calculate_scores.py \
  --metrics-file evaluation-metrics.json \
  --output evaluation-summary.json
```

### 3. Generate Report

```bash
python ../../../tests/evaluation/scripts/generate_report.py \
  --metrics evaluation-summary.json \
  --output evaluation-report.md
```

### 4. Compare with Baseline

```bash
python ../../../tests/evaluation/scripts/compare_with_baseline.py \
  --current evaluation-summary.json \
  --baseline ../../../tests/evaluation/baselines/latest-baseline.json \
  --output regression-report.json
```

## Customization

### Adding New Test Cases

1. Edit `datasets/golden_dataset.json`:

```json
{
  "id": "custom-001-en",
  "category": "irrigation",
  "language": "en",
  "input": {
    "query": "Your custom query",
    "context": {}
  },
  "expected_output": {
    "response": "Expected response",
    "agents": ["irrigation_advisor"],
    "key_points": ["key1", "key2"],
    "safety_constraints": []
  },
  "evaluation_criteria": {
    "min_similarity": 0.75,
    "required_keywords": [],
    "forbidden_keywords": [],
    "max_latency_ms": 5000
  }
}
```

2. Validate:

```bash
python scripts/validate_dataset.py
```

### Adjusting Thresholds

Edit `conftest.py` to modify evaluation thresholds:

```python
@pytest.fixture(scope="session")
def evaluation_config() -> Dict[str, Any]:
    return {
        "min_accuracy_threshold": 0.85,  # Change this
        "max_latency_ms": 5000,          # Change this
        "min_safety_score": 0.95,        # Change this
        # ...
    }
```

### Custom Similarity Methods

Modify `evaluator.py` to add custom similarity calculations:

```python
class SimilarityCalculator:
    def calculate_similarity(self, generated, expected, method="hybrid"):
        # Add your custom method here
        if method == "custom":
            return self._custom_similarity(generated, expected)
        # ...
```

## Troubleshooting

### Issue: Import Errors

**Problem**: Cannot import evaluation modules

**Solution**:

```bash
# Add to PYTHONPATH
export PYTHONPATH=/home/user/sahool-unified-v15-idp:$PYTHONPATH

# Or install in development mode
cd /home/user/sahool-unified-v15-idp
pip install -e .
```

### Issue: Sentence Transformers Model Download

**Problem**: Model download fails or is slow

**Solution**:

```python
# Pre-download the model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
```

Or set cache directory:

```bash
export TRANSFORMERS_CACHE=/path/to/cache
export SENTENCE_TRANSFORMERS_HOME=/path/to/cache
```

### Issue: API Rate Limits

**Problem**: Tests fail due to API rate limits

**Solution**:

1. Use mocked responses for rapid testing
2. Implement rate limiting in tests
3. Use local models when possible

### Issue: Low Similarity Scores

**Problem**: All tests failing with low similarity

**Solution**:

1. Check expected outputs are realistic
2. Verify similarity calculation method
3. Review agent prompt quality
4. Consider adjusting `min_similarity` threshold

### Issue: High Latency

**Problem**: Tests timeout or fail latency checks

**Solution**:

1. Increase timeout in `pytest.ini`
2. Optimize agent code
3. Check network connectivity
4. Review external service dependencies

## Best Practices

### 1. Test Before Commit

Always run evaluation tests locally before pushing:

```bash
pytest ../../../tests/evaluation/ -v
```

### 2. Keep Golden Dataset Updated

Regularly review and update golden dataset with:

- New use cases
- Edge cases
- Real user queries
- Both languages (Arabic/English)

### 3. Monitor Baseline Drift

Review baseline comparisons to understand:

- Performance trends
- Impact of changes
- Regression sources

### 4. Document Changes

When modifying evaluation:

- Update README.md
- Document threshold changes
- Explain new test cases
- Update baseline expectations

### 5. Version Control

- Commit golden datasets
- Track baseline history
- Document evaluation changes
- Review evaluation in PRs

## Continuous Improvement

### Weekly Tasks

- [ ] Review failed test cases
- [ ] Update golden dataset with new examples
- [ ] Check for performance regressions
- [ ] Monitor evaluation trends

### Monthly Tasks

- [ ] Comprehensive evaluation review
- [ ] Update baselines
- [ ] Adjust thresholds if needed
- [ ] Review and refine safety rules
- [ ] Add missing test coverage

### Quarterly Tasks

- [ ] Major evaluation framework updates
- [ ] Review Google AgentOps best practices
- [ ] Benchmark against industry standards
- [ ] Conduct user feedback sessions
- [ ] Update evaluation documentation

## Support

For help with the evaluation pipeline:

1. Check this documentation
2. Review test logs and error messages
3. Consult the AI team
4. Create an issue in the repository

## Resources

- [Main README](README.md)
- [Google AgentOps Whitepaper](https://research.google/pubs/agentops/)
- [LangChain Evaluation Guide](https://python.langchain.com/docs/guides/evaluation)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Last Updated**: December 2025
**Version**: 1.0.0
