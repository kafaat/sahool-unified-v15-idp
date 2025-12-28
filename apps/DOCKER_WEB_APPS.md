# Docker Setup for Web Applications

This document describes the Docker configuration for SAHOOL's web applications.

## Applications

### 1. Web Application (apps/web)
- **Port**: 3000
- **Description**: Main web application for SAHOOL agricultural platform
- **Tech Stack**: Next.js 15, React 19, TypeScript

### 2. Admin Dashboard (apps/admin)
- **Port**: 3001
- **Description**: Administrative dashboard for platform management
- **Tech Stack**: Next.js 15, React 19, TypeScript

## Files Created/Modified

### apps/web
- ✅ `Dockerfile` - Multi-stage Docker build configuration
- ✅ `.dockerignore` - Excludes unnecessary files from Docker context
- ✅ `next.config.js` - Updated with `output: 'standalone'` for Docker deployment
- ✅ `public/` - Created public directory with .gitkeep

### apps/admin
- ✅ `Dockerfile` - Already exists, verified
- ✅ `.dockerignore` - Already exists, verified
- ✅ `next.config.js` - Already configured with `output: 'standalone'`
- ✅ `public/` - Created public directory with .gitkeep

## Docker Compose Configuration (Optional)

To add these applications to your `docker-compose.yml`, add the following services:

```yaml
  # Main Web Application
  web:
    build:
      context: .
      dockerfile: apps/web/Dockerfile
      args:
        - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}
    container_name: sahool-web
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}
      - NEXT_PUBLIC_APP_NAME=SAHOOL
      - NEXT_PUBLIC_APP_VERSION=16.0.0
    ports:
      - "3000:3000"
    depends_on:
      kong:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000', (r) => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    networks:
      - sahool-network

  # Admin Dashboard
  admin:
    build:
      context: .
      dockerfile: apps/admin/Dockerfile
      args:
        - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}
    container_name: sahool-admin
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}
    ports:
      - "3001:3001"
    depends_on:
      kong:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3001', (r) => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    networks:
      - sahool-network
```

## Building the Images

### Build Web Application
```bash
docker build -f apps/web/Dockerfile -t sahool-web:latest .
```

### Build Admin Dashboard
```bash
docker build -f apps/admin/Dockerfile -t sahool-admin:latest .
```

### Build Both Applications
```bash
docker build -f apps/web/Dockerfile -t sahool-web:latest .
docker build -f apps/admin/Dockerfile -t sahool-admin:latest .
```

## Running Standalone Containers

### Run Web Application
```bash
docker run -d \
  --name sahool-web \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  sahool-web:latest
```

### Run Admin Dashboard
```bash
docker run -d \
  --name sahool-admin \
  -p 3001:3001 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  sahool-admin:latest
```

## Environment Variables

### Web Application
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_APP_NAME` - Application name (default: SAHOOL)
- `NEXT_PUBLIC_APP_VERSION` - Application version (default: 16.0.0)
- `NODE_ENV` - Environment mode (production/development)

### Admin Dashboard
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)
- `NODE_ENV` - Environment mode (production/development)

## Build Configuration

Both applications use Next.js 15's standalone output mode, which:
- Creates a minimal production build
- Includes only necessary dependencies
- Reduces image size significantly
- Improves startup time

### Dockerfile Structure
Both Dockerfiles follow a multi-stage build pattern:

1. **base** - Node.js 20 Alpine base image
2. **deps** - Install dependencies using npm workspaces
3. **builder** - Build shared packages and the application
4. **runner** - Production image with minimal footprint

### Monorepo Support
The Dockerfiles are configured to work with the npm workspaces monorepo structure:
- Copies root package files for workspace resolution
- Installs all workspace dependencies
- Builds shared packages before the application
- Uses Next.js standalone mode for optimal production builds

## Verification

After building, verify the setup:

```bash
# Check image size
docker images | grep sahool

# Check if containers are running
docker ps | grep sahool

# Check logs
docker logs sahool-web
docker logs sahool-admin

# Test endpoints
curl http://localhost:3000
curl http://localhost:3001
```

## Troubleshooting

### Build fails with dependency errors
- Ensure all shared packages are properly defined in workspaces
- Run `npm install` at the root level first
- Check that package.json files are correctly copied in Dockerfile

### Container fails to start
- Check environment variables are set correctly
- Verify the API URL is accessible from the container
- Review container logs: `docker logs sahool-web`

### Port already in use
- Change the host port mapping: `-p 3002:3000` instead of `-p 3000:3000`
- Or stop the conflicting service

## Production Considerations

1. **Use build arguments for API URLs** during build time
2. **Set appropriate memory limits** based on your load
3. **Enable health checks** to ensure container availability
4. **Use volumes for logs** if needed
5. **Configure reverse proxy** (nginx/traefik) for SSL/TLS
6. **Set up monitoring** for container metrics

## Security

- Both applications run as non-root user (nextjs:nodejs)
- No privileged access required
- Environment files are excluded via .dockerignore
- Minimal attack surface with standalone builds

## Performance

- Standalone mode reduces image size by ~40%
- Uses SWC compiler for faster builds
- Optimized for production with minimal dependencies
- Health checks ensure container availability
