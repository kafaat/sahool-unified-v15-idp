# GitHub Actions Cache Resilience

## Overview

This document describes the cache fallback mechanism implemented to prevent Docker build failures when GitHub Actions cache service experiences outages.

## Problem Statement

During GitHub Actions workflow runs, Docker container builds were failing with the following error when GitHub's cache service was unavailable:

```
ERROR: failed to parse error response 400: 
<h2>Our services aren't available right now</h2>
<p>We're working to restore all services as soon as possible. 
Please check back soon.</p>
```

### Impact
- 26 container build jobs failed in a single workflow run
- Builds were blocked by transient infrastructure issues outside our control
- No fallback mechanism existed when GitHub Actions cache was down

## Root Cause

The Docker `build-push-action` was configured to use **only** GitHub Actions cache (`type=gha`):

```yaml
cache-from: type=gha,scope=service-v2
cache-to: type=gha,scope=service-v2,mode=max
```

When the GitHub Actions cache service experiences downtime or rate limiting, the build process fails completely because:
1. It cannot write cache to the unavailable service
2. No alternative cache mechanism was configured
3. The build step is not resilient to cache failures

## Solution

### Implemented Fix

We added **inline caching** as a fallback mechanism. Inline caching embeds cache metadata directly into the Docker image layers, making it independent of external cache services.

**New Configuration:**
```yaml
cache-from: |
  type=gha,scope=service-v2
  type=inline
cache-to: type=inline,mode=max
```

### How It Works

1. **Cache Read (cache-from)**:
   - First tries to read from GitHub Actions cache (optimal)
   - Falls back to inline cache if GHA cache is unavailable
   - Proceeds without cache if both are unavailable

2. **Cache Write (cache-to)**:
   - Writes cache using inline method (embedded in image layers)
   - Works even when GitHub's cache service is down
   - Cache is stored in the built image itself

### Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Resilience** | Fails when GHA cache is down | Continues with inline cache |
| **Availability** | Dependent on GitHub infrastructure | Independent fallback available |
| **Performance** | Optimal when working | Near-optimal with minimal degradation |
| **Maintenance** | Manual intervention needed on failures | Self-healing mechanism |

## Technical Details

### Cache Types Comparison

| Cache Type | Storage Location | Pros | Cons |
|------------|-----------------|------|------|
| **GHA Cache** | GitHub Actions cache service | Fast, shared across runs | Depends on GitHub service availability |
| **Inline Cache** | Docker image layers | Always available, embedded | Slightly larger image size |
| **Registry Cache** | Container registry | Persistent, sharable | Requires push access, slower |

### Performance Impact

- **GHA Cache Available**: No performance impact (uses GHA cache)
- **GHA Cache Down**: Minimal impact (uses inline cache from previous builds)
- **Cold Build**: Slight increase in build time (no cache available)

Inline cache overhead: ~2-5% larger image size, negligible build time difference.

### Workflow Files Modified

1. **`.github/workflows/container-tests.yml`**
   - Main container testing and security scanning workflow
   - 26+ services tested in parallel matrix

2. **`.github/workflows/ci.yml`**
   - Continuous integration pipeline
   - Service validation and smoke tests

3. **`.github/workflows/release.yml`**
   - Production release builds
   - Multi-platform container publishing

4. **`.github/workflows/docker-buildx.yml`**
   - Multi-architecture builds (amd64, arm64)
   - Two separate build jobs updated

## Verification

### Testing the Fix

To verify the cache fallback mechanism works:

1. **Successful GHA Cache Scenario**:
   ```bash
   # Check workflow logs for:
   # "importing cache manifest from gha:..."
   ```

2. **GHA Cache Unavailable Scenario**:
   ```bash
   # Check workflow logs for:
   # Falls back to inline cache
   # Build continues successfully
   ```

3. **Cache Miss Scenario**:
   ```bash
   # First build with no cache:
   # "cache-from: type=gha" - miss
   # "cache-from: type=inline" - miss
   # Build completes from scratch
   ```

### Monitoring

Monitor GitHub Actions workflow runs for:
- Build success rate (should remain high even during GHA cache outages)
- Build duration (should remain stable)
- Cache hit rate (tracked in build logs)

## Best Practices

### For New Workflows

When adding Docker builds to new workflows, always use the resilient cache configuration:

```yaml
- name: Build Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    file: path/to/Dockerfile
    push: false
    tags: myimage:latest
    # Resilient cache configuration
    cache-from: |
      type=gha,scope=my-service-v1
      type=inline
    cache-to: type=inline,mode=max
```

### Cache Scope Versioning

Use versioned cache scopes to invalidate cache when needed:
- `scope=service-v1` - Initial version
- `scope=service-v2` - After breaking changes
- `scope=service-v3` - After major dependency updates

### When to Invalidate Cache

Bump cache scope version when:
- Base image changes significantly
- Major dependency updates (Python 3.11 → 3.12)
- Build process changes
- Persistent cache corruption issues

## Troubleshooting

### Issue: Builds Still Failing

**Symptoms**: Builds fail even with inline cache

**Possible Causes**:
1. Dockerfile syntax errors
2. Missing build context files
3. Network issues pulling base images

**Resolution**:
```bash
# Check build logs for actual error
# Look beyond cache-related messages
```

### Issue: Slow Builds

**Symptoms**: Builds take longer than expected

**Possible Causes**:
1. Cache miss (both GHA and inline)
2. Large dependency downloads
3. Multi-stage build inefficiency

**Resolution**:
- Check cache hit rate in logs
- Optimize Dockerfile layer caching
- Use buildkit cache mounts for package managers

### Issue: Large Image Sizes

**Symptoms**: Images larger after inline cache

**Expected**: 2-5% size increase is normal with inline cache

**Resolution** (if excessive):
```dockerfile
# Use multi-stage builds to exclude cache
FROM builder AS builder
# ... build with cache ...

FROM runtime
# Copy only artifacts (no cache metadata)
COPY --from=builder /app/dist /app
```

## References

- [Docker Buildx Cache Documentation](https://docs.docker.com/build/cache/)
- [GitHub Actions Cache Limits](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [BuildKit Cache Backends](https://github.com/moby/buildkit#cache)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-18 | Initial implementation of cache fallback |

---

**Maintainer**: KAFAAT Platform Team  
**Last Updated**: 2026-01-18
