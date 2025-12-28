# Agent Evaluation Pipeline - Quick Reference
# خط أنابيب تقييم الوكلاء - مرجع سريع

## File Locations

```
/home/user/sahool-unified-v15-idp/
├── .github/workflows/agent-evaluation.yml
└── tests/evaluation/
    ├── README.md, SETUP.md, IMPLEMENTATION_SUMMARY.md
    ├── conftest.py, evaluator.py, test_agent_behavior.py
    ├── datasets/golden_dataset.json
    └── scripts/*.py
```

## Common Commands

### Run Tests
```bash
# Full evaluation
cd apps/services/ai-advisor
pytest ../../../tests/evaluation/ -v

# Specific category
pytest ../../../tests/evaluation/ -v -m arabic
pytest ../../../tests/evaluation/ -v -m safety

# With coverage
pytest ../../../tests/evaluation/ --cov=src --cov-report=html
```

### Generate Reports
```bash
cd apps/services/ai-advisor

# Calculate scores
python ../../../tests/evaluation/scripts/calculate_scores.py \
  --metrics-file evaluation-metrics.json \
  --output evaluation-summary.json

# Generate markdown report
python ../../../tests/evaluation/scripts/generate_report.py \
  --metrics evaluation-summary.json \
  --output evaluation-report.md

# Compare with baseline
python ../../../tests/evaluation/scripts/compare_with_baseline.py \
  --current evaluation-summary.json \
  --baseline ../../../tests/evaluation/baselines/latest-baseline.json \
  --output regression-report.json
```

### Dataset Management
```bash
cd tests/evaluation

# Create dataset
python scripts/create_golden_dataset.py

# Validate dataset
python scripts/validate_dataset.py

# Verify setup
./verify_setup.sh
```

## Evaluation Metrics

| Metric | Weight | Target | Blocks Merge |
|--------|--------|--------|--------------|
| Overall Score | - | ≥85% | Yes |
| Accuracy | 50% | ≥85% | Yes |
| Latency | 25% | <5000ms | Yes |
| Safety | 25% | ≥95% | Yes |

## Test Markers

```bash
pytest -m evaluation  # All evaluation tests
pytest -m golden      # Golden dataset tests
pytest -m arabic      # Arabic language tests
pytest -m english     # English language tests
pytest -m latency     # Latency tests
pytest -m safety      # Safety tests
```

## GitHub Actions

Triggers automatically on:
- PRs to `apps/services/ai-advisor/**`
- PRs to `tests/evaluation/**`

Manual trigger:
```bash
gh workflow run agent-evaluation.yml
```

## Files and Sizes

| File | Size | Purpose |
|------|------|---------|
| agent-evaluation.yml | 12KB | CI/CD workflow |
| conftest.py | 18KB | Pytest fixtures |
| evaluator.py | 22KB | Evaluation engine |
| test_agent_behavior.py | 25KB | Test cases |
| README.md | 13KB | Main docs |
| SETUP.md | 19KB | Setup guide |

## Troubleshooting

**Import errors**:
```bash
export PYTHONPATH=/home/user/sahool-unified-v15-idp:$PYTHONPATH
```

**Model downloads**:
```bash
export TRANSFORMERS_CACHE=/path/to/cache
```

**Low scores**:
- Check expected outputs in golden dataset
- Review similarity threshold
- Verify agent prompt quality

## Documentation

- Main: `tests/evaluation/README.md`
- Setup: `tests/evaluation/SETUP.md`
- Details: `tests/evaluation/IMPLEMENTATION_SUMMARY.md`

## Support

- GitHub Issues
- AI Team
- Test logs: `apps/services/ai-advisor/*.log`

---
Quick Reference v1.0 | December 2025
