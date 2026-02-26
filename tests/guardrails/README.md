# Guardrails Tests

Tests for the AI safety guardrails system (`shared/guardrails/`). Guardrails protect the platform from prompt injection, PII leakage, toxic content, hallucinations, and off-topic requests. These tests validate all input/output filtering layers.

## Running

```bash
# All guardrails tests
pytest tests/guardrails/ -v

# Basic pattern tests (no shared dependencies)
pytest tests/guardrails/test_basic.py -v

# Full filter tests (requires shared.guardrails)
pytest tests/guardrails/test_filters.py -v

# Via Makefile
make test-python -k guardrails
```

## Test Files

### `test_basic.py`

Pattern-matching tests using regex fixtures — runs with zero dependencies beyond Python stdlib:

- **Prompt injection detection** — patterns like `ignore all instructions`, `forget everything`, `disregard commands`
- **PII detection** — email addresses, Saudi/Middle East phone numbers (`+966`, `00966`)
- **Topic filtering** — allowed agricultural topics (Arabic + English), blocked dangerous topics
- **Toxicity keyword detection** — blocked terms in both Arabic and English
- **Content truncation** — maximum character length enforcement
- **Hallucination indicators** — confidence qualifier patterns (`probably`, `might be`, `I think`)

All tests use `@pytest.fixture` for pattern/keyword sets to allow easy extension.

### `test_filters.py`

Full integration tests against `shared.guardrails` module:

**PolicyManager**
- `get_user_trust_level()` — ADMIN, PREMIUM, TRUSTED, STANDARD tier assignment based on roles and verification status

**InputFilter**
- Prompt injection detection and blocking
- PII scrubbing from user inputs
- Agricultural topic scope enforcement
- Input length and encoding validation

**OutputFilter**
- Hallucination detection in LLM responses
- PII removal from generated outputs
- Safe content level enforcement (`ContentSafetyLevel`)

**Safety Components**
- `PromptInjectionDetector` — pattern and embedding-based detection
- `PIIDetector` — entity recognition for names, IDs, phone numbers
- `ToxicityFilter` — multilingual toxicity classification
- `SafetyContentChecker` — combined safety gate with `TrustLevel` weighting
- `HallucinationDetector` — confidence and factual consistency checks
- `sanitize_input()` / `sanitize_output()` — convenience functions

## Trust Levels

```python
class TrustLevel(Enum):
    STANDARD = "standard"   # New unverified users — strictest filtering
    TRUSTED  = "trusted"    # Verified accounts — reduced friction
    PREMIUM  = "premium"    # Paid subscribers — extended limits
    ADMIN    = "admin"      # Platform admins — minimal guardrails
```

## Related

- Implementation: `shared/guardrails/`
- AI guardrails: `shared/ai/guardrails/`
- Unit tests: `tests/unit/test_guardrails.py`, `tests/unit/shared/test_guardrails_input_filter.py`
- CI: `.github/workflows/ci-ai-rag-security.yml`
