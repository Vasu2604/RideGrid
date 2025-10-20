# 🚀 START HERE - RideGrid Setup

## Welcome! This is your entry point.

### ⚡ TL;DR - Get Running Now

```bash
# From the project root
./scripts/setup.sh
```

That's it! The script will:
- ✅ Auto-detect what you have (Docker, Python, Node.js)
- ✅ Choose the best deployment mode
- ✅ Set everything up automatically
- ✅ Tell you exactly what to do next

---

## 🎯 What Mode Will You Get?

### If You Have Docker ✅
**→ Docker Mode (Recommended)**
- Everything runs in containers
- Zero local dependencies needed
- Production-like environment
- Just run `./scripts/setup.sh`

### If You DON'T Have Docker ❌
**→ Local Mode**
- Requires Python 3.11+ and Node.js 20+
- Services run on your machine
- Good for development
- Just run `./scripts/setup.sh`

**The script adapts automatically!**

---

## 📋 What You Need

### Minimum (one of these):
- **Option A**: Docker Desktop
- **Option B**: Python 3.11+ AND Node.js 20+

### That's it! 
No PostgreSQL, Redis, or Kafka installation required - they run in Docker if available, or the system adapts.

---

## 🏃 Quick Start Steps

### 1. Run Setup
```bash
./scripts/setup.sh
```

### 2. Follow the Output
The script will tell you exactly what to do next based on your system.

### 3. Access the App
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8001  
- **Grafana**: http://localhost:3001 (admin/admin)

---

## 📚 Documentation Quick Links

| Document | When to Read |
|----------|-------------|
| **[QUICK_START.md](QUICK_START.md)** | After setup - learn what to do |
| **[DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)** | Understand all deployment modes |
| **[README.md](README.md)** | Full project documentation |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | See what was built |
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | Detailed setup guide |

---

## ❓ Common Questions

**Q: Do I need to install PostgreSQL/Redis/Kafka?**  
A: No! They run in Docker, or the system adapts to what you have.

**Q: What if I don't have Docker?**  
A: The script will use local mode if you have Python + Node.js.

**Q: What if I have nothing?**  
A: The script will tell you exactly what to install.

**Q: How do I stop everything?**  
A: Run `./scripts/stop-all.sh` or `cd deploy/docker-compose && docker-compose down`

**Q: Something broke, what now?**  
A: Check [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md) troubleshooting section.

---

## 🎯 Your Next 5 Minutes

1. **Run setup** (30 seconds)
   ```bash
   ./scripts/setup.sh
   ```

2. **Open browser** (10 seconds)
   - Go to http://localhost:3000

3. **Create a test ride** (1 minute)
   ```bash
   curl -X POST http://localhost:8001/api/rides \
     -H "Content-Type: application/json" \
     -d '{
       "rider_id": "test",
       "origin": {"latitude": 37.7749, "longitude": -122.4194},
       "destination": {"latitude": 37.7849, "longitude": -122.4094},
       "ride_type": "ECONOMY",
       "passenger_count": 1,
       "payment_method_id": "pm_test"
     }'
   ```

4. **View in dashboard** (1 minute)
   - Click Dashboard link at http://localhost:3000
   - See real-time metrics

5. **Check Grafana** (1 minute)
   - Go to http://localhost:3001
   - Login: admin/admin
   - View "RideGrid - System Overview" dashboard

---

## ✅ Success Checklist

After setup, you should be able to:

- [ ] See the landing page at http://localhost:3000
- [ ] Get `{"status":"healthy"}` from http://localhost:8001/health
- [ ] Create a ride via curl command above
- [ ] See live metrics in dashboard
- [ ] View Grafana dashboards

**All checked?** 🎉 You're good to go!

---

## 🆘 Quick Troubleshooting

### Setup script fails
```bash
# Check what you have
docker --version
python3 --version
node --version

# If missing, install:
# Docker: https://docker.com
# Python: https://python.org
# Node: https://nodejs.org
```

### Port conflicts
```bash
# Kill processes on busy ports
lsof -ti:3000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
```

### Services won't start
```bash
# Check logs
tail -f logs/*.log

# Or if using Docker
cd deploy/docker-compose
docker-compose logs -f
```

---

## 🎓 Learn More

Once you're up and running:

1. **Explore the Architecture**
   - Read [docs/architecture.md](docs/architecture.md)
   - Understand the microservices
   - Learn about event-driven patterns

2. **Test Performance**
   ```bash
   k6 run load/k6/load-test.js
   ```

3. **Customize**
   - Modify matching algorithms in `services/matching-engine/`
   - Enhance UI in `web/ops-console/`
   - Add new metrics

4. **Deploy to Production**
   ```bash
   make deploy-k8s
   ```

---

## 💡 Pro Tips

1. **First time?** Use Docker mode - it's the easiest
2. **Developing?** Use local mode - easier debugging
3. **Stuck?** Check [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)
4. **Want details?** Read [README.md](README.md)
5. **See what's built?** Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

<div align="center">

## Ready? Let's Go! 🚀

```bash
./scripts/setup.sh
```

</div>





