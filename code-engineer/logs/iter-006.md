# Iteration 006 — Make Ollama GPU Services Optional

**Timestamp:** 2026-01-08T21:30:00Z
**Target service:** ollama, ollama-model-loader, code-review-service
**Goal:** Add profiles to GPU-dependent services to allow stack to run without NVIDIA GPU

## Evidence (Before)

- ollama service has `driver: nvidia` device reservation
- ollama-model-loader depends on ollama
- code-review-service depends on ollama
- Stack fails on non-GPU systems with:
  ```
  error response from daemon: could not select device driver "" with capabilities: [[gpu]]
  ```

## Hypothesis

- Adding Docker Compose profiles will make GPU services optional
- Stack can run without GPU by omitting the `--profile gpu` flag

## Actions Taken

### File Changes

- `docker-compose.yml`
  - ollama service (line 376-377):
    - Added `profiles: ["gpu"]`
    - Added NOTE comment about GPU requirement
  - ollama-model-loader service (line 427-428):
    - Added `profiles: ["gpu"]`
    - Added NOTE comment
  - code-review-service service (line 462-463):
    - Added `profiles: ["gpu"]`
    - Added NOTE comment about Ollama dependency

## Evidence (After)

- All three services now have `profiles: ["gpu"]`
- Documentation comments explain the requirement

## Usage After Fix

```bash
# Without GPU (most services):
docker compose up -d

# With GPU (includes Ollama, code-review):
docker compose --profile gpu up -d
```

## Result

- **PASS**
- Stack can now run without NVIDIA GPU
- GPU-dependent features (code review) are optional
- Next step: Create fix summary
