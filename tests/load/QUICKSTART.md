# Quick Start Guide - SAHOOL Load Testing

Get started with load testing in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- OR k6 installed locally

## 🚀 Quick Start (5 minutes)

### Option 1: Using Docker (Recommended)

```bash
# 1. Navigate to load test directory
cd tests/load

# 2. Start Grafana dashboard (optional but recommended)
make setup-grafana

# 3. Run smoke test to verify everything works
make docker-smoke

# 4. View results in Grafana
open http://localhost:3030
# Login: admin/admin

# 5. Run load test
make docker-load
```

### Option 2: Using Local k6

```bash
# 1. Install k6 (macOS)
brew install k6

# 2. Navigate to load test directory
cd tests/load

# 3. Run smoke test
make smoke

# 4. Run load test
make load
```

## 📊 View Results

### In Terminal
Results are printed after each test with key metrics:
- Response times (P95, P99)
- Error rate
- Request rate
- Check success rate

### In Grafana (if using Docker)
1. Open http://localhost:3030
2. Login: admin/admin
3. Browse dashboards for real-time metrics

### In Files
Results are saved in `results/` directory:
```bash
ls -lh results/
```

## 🎯 Common Commands

```bash
# Quick smoke test
make smoke

# Full load test (10 minutes)
make load

# Check if services are ready
make check

# Run all tests
make all

# Clean up results
make clean

# Stop Grafana
make stop-grafana
```

## 🔧 Configuration

Edit `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
nano .env
```

Key settings:
```bash
FIELD_SERVICE_URL=http://localhost:8080
WEATHER_URL=http://localhost:8092
BILLING_URL=http://localhost:8089
```

## 📝 Test Types

| Test | Duration | VUs | Command |
|------|----------|-----|---------|
| Smoke | 1 min | 1 | `make smoke` |
| Load | 10 min | 50 | `make load` |
| Stress | 15 min | 200 | `make stress` |
| Spike | 8 min | 200 | `make spike` |
| Soak | 2 hours | 20 | `make soak` |

## ❓ Troubleshooting

**Services not reachable?**
```bash
# Check if SAHOOL services are running
docker ps | grep sahool

# Verify health
make check
```

**Tests failing?**
```bash
# Run in debug mode
k6 run --http-debug scenarios/smoke.js
```

**Need help?**
```bash
# Show all commands
make help

# Read full documentation
cat README.md
```

## 📚 Next Steps

1. **Read the full README.md** for detailed documentation
2. **Review test scenarios** in `scenarios/` directory
3. **Customize tests** by editing JavaScript files
4. **Set up CI/CD** to run tests automatically
5. **Monitor trends** over time using Grafana

## 🎓 Learning Resources

- [k6 Documentation](https://k6.io/docs/)
- [Load Testing Guide](https://k6.io/docs/testing-guides/)
- See `README.md` for comprehensive guide

---

**Ready to test?** Start with:
```bash
make smoke
```
