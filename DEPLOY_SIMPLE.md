# Deploy LegalDocSimplifier Live in 3 Steps ⚡

Everything is ready to deploy! Follow these exact steps.

## STEP 1: Deploy Backend (Render) - 5 minutes

**1. Go here:** https://render.com

**2. Sign up** with GitHub (or log in if you have account)

**3. After login, click:** New → Web Service

**4. Connect your GitHub repo:**
   - Search for: `LegalDocSimplifier`
   - Select: `zortex0p/LegalDocSimplifier`
   - Click "Connect"

**5. Fill in the settings:**
```
Name: lexplain-api
Environment: Python 3
Build Command: pip install -r backend/requirements.txt
Start Command: gunicorn --chdir backend app:app
Plan: Free (recommended)
```

**6. Add Environment Variables (click "Advanced"):**

Add these 3 variables:
```
FLASK_ENV = production
DATABASE_URL = sqlite:///legal_documents.db
ANTHROPIC_API_KEY = sk-ant-PASTE_YOUR_KEY_HERE
```

**To get ANTHROPIC_API_KEY:**
- Visit: https://console.anthropic.com/api-keys
- Create new key or copy existing
- Paste the `sk-ant-...` value into Render

**7. Click "Create Web Service"**

⏳ Wait 2-5 minutes for deployment...

**✅ When done, you'll see a URL like:**
```
https://lexplain-api.onrender.com
COPY THIS URL!
```

---

## STEP 2: Update Frontend Code

In your project, edit `frontend/index.html`

Find this line (around line 930):
```javascript
: 'https://lexplain-api.onrender.com/api/simplify'; // UPDATE THIS with your Render URL
```

**Replace** `lexplain-api.onrender.com` with your actual Render URL from Step 1.

**Example:** If your Render URL is `https://my-api-abc123.onrender.com`, change it to:
```javascript
: 'https://my-api-abc123.onrender.com/api/simplify';
```

**Then run these commands in terminal:**
```bash
cd c:\Users\madha\LegalDocSimplifier
git add -A
git commit -m "Update backend URL for production"
git push origin main
```

---

## STEP 3: Deploy Frontend (Vercel) - 5 minutes

**1. Go here:** https://vercel.com

**2. Sign up** with GitHub (or log in)

**3. After login, click:** Add New → Project

**4. Select your repository:**
   - Search: `LegalDocSimplifier`
   - Click it
   - Click "Import"

**5. Leave settings as default, click "Deploy"**

⏳ Wait 1-2 minutes...

**✅ When done, you'll see:**
```
Congratulations! Your project is live.
https://lexplain.vercel.app (or similar)
COPY THIS URL!
```

---

## STEP 4: Test It!

**Paste in browser:**
```
https://your-render-url/api/health
```

You should see:
```json
{"status": "healthy", ...}
```

**Then visit your Vercel URL** and try analyzing a document!

---

## Your Live Website 🎉

**Frontend:** https://lexplain.vercel.app (or your custom domain)
**Backend:** https://your-render-url (from Step 1)

Share the frontend URL with anyone!

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "Cannot connect to API" | Update frontend code with correct Render URL |
| "API key error" | Get fresh key from https://console.anthropic.com |
| "Render cold start slow" | Normal! Free tier sleeps after 15 min. First request takes 30sec |
| "Vercel shows loading" | Might be waiting for Render. Refresh page |

---

## Total Cost
- **Free version:** $0/month (with cold starts)
- **Upgrade Render:** +$7/month for always-online
- **API usage:** Usually <$1/month

---

**That's it! You're live!** 🚀

Estimated total time: 10-15 minutes
