# Deployment Guide - Vercel + Render

Your LegalDocSimplifier is ready to deploy online! Follow these steps to get it live.

## Part 1: Deploy Backend to Render

### Step 1: Create Render Account
1. Go to https://render.com
2. Click "Sign up"
3. Sign up with GitHub (recommended for easy integration)

### Step 2: Deploy Backend
1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Select your GitHub repository: `zortex0p/LegalDocSimplifier`
3. Configure the service:
   - **Name**: `lexplain-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `gunicorn --chdir backend app:app`
   - **Plan**: Free (or paid if you prefer)

### Step 3: Add Environment Variables
In the Render dashboard, add these environment variables:
```
FLASK_ENV=production
DATABASE_URL=sqlite:///legal_documents.db
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE
```

**Important**: Get your Anthropic API key from https://console.anthropic.com/api-keys

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait for build and deployment (2-5 minutes)
3. Copy your backend URL (e.g., `https://lexplain-api.onrender.com`)

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Create Vercel Account
1. Go to https://vercel.com
2. Click "Sign up"
3. Sign up with GitHub

### Step 2: Import Project
1. Click **"Add New..."** → **"Project"**
2. Select your GitHub repository: `zortex0p/LegalDocSimplifier`
3. Configure:
   - **Project Name**: `lexplain`
   - **Framework**: `Other` (static site)
   - **Root Directory**: `./` (or leave empty)

### Step 3: Add Environment Variables
1. Go to **Settings** → **Environment Variables**
2. Add:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: Your Render backend URL (e.g., `https://lexplain-api.onrender.com`)

### Step 4: Deploy
1. Click **"Deploy"**
2. Wait for deployment (1-2 minutes)
3. You'll get a live URL like `https://lexplain.vercel.app`

---

## Part 3: Update Frontend with Backend URL

Since Vercel doesn't support environment variables in static HTML files by default, you have two options:

### Option A: Manual Update (Simple)
1. Edit `frontend/index.html`
2. Change this line:
   ```javascript
   const apiUrl = window.location.hostname === 'localhost' 
     ? 'http://localhost:5000/api/simplify'
     : `https://YOUR-RENDER-API-URL/api/simplify`
   ```
3. Replace `YOUR-RENDER-API-URL` with your actual Render URL
4. Commit and push to GitHub

### Option B: Use Environment Variables (Advanced)
Create a `src/config.js` file or use a build step with environment variables.

---

## Verification

### Test Your Deployment

1. **Check Backend**:
   ```
   https://lexplain-api.onrender.com/api/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **Check Frontend**:
   Visit your Vercel URL in a browser
   Try analyzing a sample document

3. **Test Full Integration**:
   - Go to your Vercel frontend
   - Paste sample legal text
   - Click "Analyze Document"
   - Should see results

---

## Troubleshooting

### Backend shows "Application Error"
- Check environment variables are set correctly
- Verify `ANTHROPIC_API_KEY` is valid
- Check Render logs for errors

### Frontend can't connect to backend
- Verify backend URL is correct in frontend code
- Check CORS is enabled (it is by default in `app.py`)
- Use browser DevTools → Network tab to see actual API calls

### Cold start slow
- Render spins down free tier apps after 15 minutes of inactivity
- This is normal - first request will be slow
- Upgrade to paid plan to keep it always running

---

## Cost Breakdown

| Service | Free Tier | Notes |
|---------|-----------|-------|
| **Render Backend** | Available | Spins down after 15 min inactivity |
| **Vercel Frontend** | Available | Unlimited deployments |
| **Anthropic API** | Pay-as-you-go | ~$3/1M tokens, cheap unless heavy use |
| **Total Monthly** | ~$5+usage | Very affordable |

---

## Domain Setup (Optional)

Want a custom domain?

### Add Custom Domain to Vercel
1. In Vercel Settings → **Domains**
2. Add custom domain
3. Follow DNS instructions

### Add Custom Domain to Render
1. In Render Services → **Settings** → **Custom Domains**
2. Add domain and update DNS

---

## Production Improvements

For production use, consider:

1. **Upgrade to PostgreSQL** instead of SQLite
   - Add `DATABASE_URL=postgresql://...` to Render env vars
   - More robust for production

2. **Use Paid Plans**
   - Render Starter (~$7/month): No cold starts
   - Vercel Pro (~$20/month): More features
   
3. **Enable HTTPS** (automatic on both platforms)

4. **Set up monitoring** with Sentry or similar

5. **Add analytics** with Plausible or Google Analytics

---

## Support

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Anthropic Docs**: https://docs.anthropic.com

Deployment takes ~8-10 minutes total. Follow the steps above and you'll be live! 🚀
