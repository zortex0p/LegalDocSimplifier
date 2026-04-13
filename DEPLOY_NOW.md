# 🚀 One-Click Deployment Guide

Follow these exact steps to get your LegalDocSimplifier live online in ~10 minutes.

---

## Step 1: Deploy Backend (Render) - 5 Minutes

### 1.1 Create Render Account
- Go to: https://render.com/register
- Sign up with GitHub (easier)

### 1.2 Deploy Backend
Click the button: **https://render.com/deploy?repo=https://github.com/zortex0p/LegalDocSimplifier**

Or manually:
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub: `zortex0p/LegalDocSimplifier`
4. Fill in:
   - **Name:** `lexplain-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `gunicorn --chdir backend app:app`
   - **Plan:** Free

### 1.3 Add Environment Variables
In Render dashboard, go to **Settings** → **Environment**:

```
FLASK_ENV=production
DATABASE_URL=sqlite:///legal_documents.db
```

**Get your Anthropic API Key:**
- Visit: https://console.anthropic.com/api-keys
- Create or copy your API key
- Add to Render:
```
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
```

### 1.4 Deploy
Click **"Create Web Service"** and wait (2-5 min)

**✅ Copy your Backend URL** (looks like `https://lexplain-api.onrender.com`)

---

## Step 2: Update Frontend with Backend URL

### 2.1 Quick Update
Edit `frontend/index.html` and find this line (~line 923):

**Replace:**
```javascript
const apiUrl = window.location.hostname === 'localhost' 
  ? 'http://localhost:5000/api/simplify'
  : `${window.location.protocol}//${window.location.hostname.replace('front-', 'back-')}/api/simplify`
    .replace('lexplain', 'lexplain-api');
```

**With:**
```javascript
const apiUrl = window.location.hostname === 'localhost' 
  ? 'http://localhost:5000/api/simplify'
  : 'https://YOUR-BACKEND-URL/api/simplify'; // Replace YOUR-BACKEND-URL with your Render URL
```

### 2.2 Example:
If your Render URL is `https://lexplain-api.onrender.com`, use:
```javascript
const apiUrl = window.location.hostname === 'localhost' 
  ? 'http://localhost:5000/api/simplify'
  : 'https://lexplain-api.onrender.com/api/simplify';
```

### 2.3 Commit & Push
```bash
cd c:\Users\madha\LegalDocSimplifier
git add frontend/index.html
git commit -m "Update API URL for production"
git push origin main
```

---

## Step 3: Deploy Frontend (Vercel) - 5 Minutes

### 3.1 Create Vercel Account
- Go to: https://vercel.com/signup
- Sign up with GitHub

### 3.2 Import Project
1. Go to https://vercel.com/dashboard
2. Click **"Add New"** → **"Project"**
3. Select: `zortex0p/LegalDocSimplifier`
4. Click **"Import"**

### 3.3 Configuration (leave defaults)
- **Project Name:** `lexplain` (or any name)
- **Framework:** `Other`
- **Root Directory:** `./`

### 3.4 Deploy
- Click **"Deploy"**
- Wait 1-2 minutes for build to complete

### 3.5 Get Your Live URL
Once deployed, Vercel shows you a URL like:
```
https://lexplain.vercel.app
```

**✅ This is your live website!**

---

## Step 4: Verify It Works

### 4.1 Test Backend Health
Open: `https://YOUR-BACKEND-URL/api/health`

You should see (or similar):
```json
{"status": "healthy", "service": "Legal Document Simplifier", "timestamp": "..."}
```

### 4.2 Test Frontend
1. Open your Vercel URL (e.g., `https://lexplain.vercel.app`)
2. Paste sample legal text in the analyzer
3. Click "Analyze Document"
4. Should see results within 5-10 seconds

### 4.3 Troubleshooting

**Backend shows error?**
- Check Render logs: Render Dashboard → Services → lexplain-api → Logs
- Verify ANTHROPIC_API_KEY is set correctly
- Make sure API key is fresh from https://console.anthropic.com/api-keys

**Frontend can't connect?**
- Browser console (F12) → Network tab → Check API calls
- Verify backend URL in frontend code matches exactly
- Both services need to be deployed first

**API returns 403/401?**
- Invalid or expired ANTHROPIC_API_KEY
- Get new key from Anthropic console

---

## Success Checklist ✅

- [ ] Backend URL from Render (e.g., `https://lexplain-api.onrender.com`)
- [ ] Frontend API URL updated in code
- [ ] Code committed and pushed to GitHub
- [ ] Vercel imported project and deployed
- [ ] Vercel shows green "Ready" status
- [ ] Render shows "Live" status
- [ ] Backend health endpoint responds
- [ ] Frontend loads in browser
- [ ] Can analyze a sample document
- [ ] See results appear on screen

---

## Your Live URLs

Once deployed, share these:

**Frontend:** https://lexplain.vercel.app (or your custom domain)
**API Health Check:** https://your-backend-url/api/health

---

## Optional: Custom Domain

Want `mysite.com` instead of `vercel.app`?

### Vercel Custom Domain:
1. In Vercel Dashboard → Your Project → Settings → Domains
2. Add your domain
3. Update DNS at your domain registrar
4. Done! (takes 5-15 min)

### Render Custom Domain:
1. In Render Services → Settings → Custom Domains
2. Add your domain
3. Update DNS
4. Done!

---

## Costs (Monthly)

| Service | Free | Cost |
|---------|------|------|
| Vercel | Unlimited static hosting | $0 |
| Render | Free tier (with 15min sleep) | $7+ for always-on |
| Anthropic API | First $5 free | $0.003 per 1K tokens |
| **Total** | Everything free | ~$0-10/month |

---

## Need Help?

**Common Issues & Fixes:**

| Issue | Fix |
|-------|-----|
| "Backend not responding" | Wait 2 min for Render cold start; check API key |
| "CORS error" | Backend URL in frontend code wrong or has typo |
| "API key error" | Get new key from https://console.anthropic.com |
| "Long response time" | Normal on free tier; upgrade to paid for instant |

---

## Next Steps After Deployment ✨

1. **Share your live URL** with friends/team
2. **Get pro API key** for unlimited analysis
3. **Add custom domain** for professional look
4. **Monitor usage** in Anthropic dashboard
5. **Upgrade to paid plans** if usage grows

---

**Your project is ready to go live! 🎉**

Estimated time: 10-15 minutes
Difficulty: Easy ⭐
