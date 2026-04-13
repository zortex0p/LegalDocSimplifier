# Quick Start Guide

Get the Legal Document Simplifier running in 5 minutes!

## ⚡ Fastest Way: Docker Compose

```bash
# 1. Clone and navigate
git clone <your-repo-url>
cd LegalDocSimplifier

# 2. Set API key
export ANTHROPIC_API_KEY=your_actual_key_from_anthropic

# 3. Start everything
docker-compose up

# 4. Open in browser
# Frontend: http://localhost:8000
# Backend: http://localhost:5000
```

Done! All services running:
- ✅ Backend API
- ✅ PostgreSQL Database
- ✅ Redis Cache

---

## 🎯 Manual Setup (For Development)

### Terminal 1: Backend

```bash
cd backend

# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY

# Run
python app.py
```

Backend ready at: **http://localhost:5000**

### Terminal 2: Frontend

```bash
cd frontend

# Option A: Python
python -m http.server 8000

# Option B: Node.js
npx http-server

# Option C: VS Code Live Server
# Just right-click index.html > Open with Live Server
```

Frontend ready at: **http://localhost:8000**

### Terminal 3: Test (Optional)

```bash
cd backend
python test_api.py
```

---

## 🔑 Getting Your API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Create an API key
4. Copy it to your `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-xxx...
```

---

## 📋 File Structure

```
LegalDocSimplifier/
├── README.md               ← You are here!
├── DEPLOYMENT.md           ← Production deployment guide
├── docker-compose.yml      ← One-command setup
│
├── backend/                ← Flask API Server
│   ├── app.py             ← Main application
│   ├── config.py          ← Configuration
│   ├── requirements.txt    ← Dependencies
│   ├── .env.example       ← Environment template
│   ├── test_api.py        ← API tests
│   ├── wsgi.py            ← Production entry point
│   ├── Dockerfile         ← Container config
│   └── README.md          ← Backend docs
│
├── frontend/              ← User Interface
│   └── index.html         ← Complete React app (single file)
│
└── assets/               ← Project assets
    └── screenshots/      ← Documentation images
```

---

## 🧪 Test Your Setup

### Option 1: Use the UI
1. Open http://localhost:8000
2. Click "Try a sample" button
3. Click "Analyze Document"
4. Wait for results!

### Option 2: Use the Command Line
```bash
curl -X POST http://localhost:5000/api/simplify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This agreement is entered between parties..."
  }'
```

### Option 3: Run Test Suite
```bash
cd backend
python test_api.py
```

---

## 🐛 Common Issues

### Issue: "ANTHROPIC_API_KEY not found"
```bash
# Check your .env file has the key
cat backend/.env | grep ANTHROPIC_API_KEY

# If missing, add it:
echo "ANTHROPIC_API_KEY=your_key" > backend/.env
```

### Issue: Port 5000 already in use
```bash
# Change port in backend/.env
PORT=5001

# Or kill the process using port 5000
lsof -ti:5000 | xargs kill -9  # macOS/Linux
```

### Issue: Frontend can't reach backend
```bash
# Check backend is running
curl http://localhost:5000/api/health

# Check CORS settings in backend/.env
CORS_ORIGINS=http://localhost:8000,http://localhost:3000
```

### Issue: LEGAL-BERT model too slow
```bash
# First run downloads ~440MB model
# Consider using GPU acceleration:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 📊 Test Documents

The app includes 4 sample documents:

1. **Rental Agreement** 🏠
   - Common lease terms
   - Security deposits & fees

2. **Employment Contract** 💼
   - Salary, non-compete, IP ownership
   - Termination terms

3. **Terms of Service** 📱
   - Data collection, liability limits
   - Modify terms & auto-renewal

4. **NDA** 🔒
   - Confidentiality obligations
   - Penalties for breach

---

## 🚀 Next Steps

### Quick Wins 🎯
- [ ] Test with sample documents
- [ ] Upload your own PDF
- [ ] Check negotiation tips
- [ ] Export analysis report

### Deploy to Production 🚀
- See [DEPLOYMENT.md](DEPLOYMENT.md) for:
  - Docker deployment
  - Heroku setup
  - AWS EC2 guide
  - Google Cloud Run

### Customize 🎨
- Modify frontend styling in `frontend/index.html`
- Add custom clause patterns in `backend/app.py`
- Extend database schema in `backend/models.py`

### Monitor Performance 📊
- Backend logs show analysis times
- Check API usage in Anthropic dashboard
- Monitor database size

---

## 💬 Getting Help

| Issue | Solution |
|-------|----------|
| Backend won't start | Check Python 3.9+, dependencies installed |
| Slow first run | LEGAL-BERT model downloads on first use |
| API errors | Check backend logs: `tail -f backend.log` |
| CORS issues | Update `CORS_ORIGINS` in `.env` |
| Database errors | Delete `.db` file to reset |

---

## 📚 Full Documentation

- **Backend**: [backend/README.md](backend/README.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **API Reference**: [backend/README.md#api-endpoints](backend/README.md#api-endpoints)
- **Configuration**: [backend/config.py](backend/config.py)

---

## ⭐ You're Ready!

Your Legal Document Simplifier is now:
- ✅ Running locally
- ✅ Connected frontend to backend
- ✅ Ready to analyze documents

Go forth and simplify those contracts! 🚀

---

**Need help?** Check the [main README.md](README.md) or [backend README](backend/README.md)
