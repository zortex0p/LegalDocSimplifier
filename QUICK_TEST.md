# Quick Test Guide

## Verify Both Servers Are Running

### 1. Test Health Endpoint
```bash
# PowerShell or CMD
curl http://127.0.0.1:5000/api/health
```

Expected output:
```json
{"status": "healthy", "service": "Legal Document Simplifier", "timestamp": "2026-04-13T..."}
```

### 2. Test Simplify Endpoint
```bash
curl -X POST http://127.0.0.1:5000/api/simplify `
  -H "Content-Type: application/json" `
  -d '{"text": "This is a rental agreement. The tenant agrees to pay $1000 per month. Landlord is not liable for damages."}'
```

Expected output:
```json
{
  "score": 50,
  "score_label": "Neutral",
  "score_desc": "..."
  "clauses": [...],
  "summary": "...",
  "negotiation_tips": [...]
}
```

## Browser Test

1. Go to http://127.0.0.1:8000
2. Click on one of the sample documents (e.g., "🏠 Rental agreement")
3. Click "🔍 Analyze Document"
4. Wait for results to appear

You should see:
- A score card showing the favorability score (0-100)
- Risk statistics (High/Medium/Low Risk counts)
- Clause-by-clause breakdown
- Overall summary
- Negotiation tips

## Common Test Scenarios

### Rental Agreement Analysis
Copy and paste this text:
```
RESIDENTIAL LEASE AGREEMENT
Tenant agrees to pay $2000/month rent.
Security deposit is 2 months rent.
Landlord may enter at any time without notice.
Tenant waives all liability claims.
Auto-renewal clause applies.
```

### Employment Contract Analysis
Copy and paste this text:
```
EMPLOYMENT AGREEMENT
Employee shall work 40 hours per week.
Non-compete clause prevents employment with competitors for 2 years.
Compensation: $50,000 annually.
Company may terminate without cause.
All intellectual property created belongs to company.
```

### Terms of Service Analysis
Copy and paste this text:
```
TERMS OF SERVICE
We may modify these terms at any time.
You agree to mandatory arbitration.
We are not liable for any damages.
Your data may be shared with third parties.
Account termination is at our sole discretion.
```

## Expected Behavior

✅ Clauses will be extracted and categorized
✅ Risk levels assigned (high=red, medium=orange, low=green)
✅ Score calculated based on overall risk
✅ Negotiation tips provided

If you added your Anthropic API key:
✅ Plain English explanations for each clause
✅ More detailed summaries
✅ Better negotiation tips

## If Something Doesn't Work

1. **Backend not responding?**
   - Check terminal where backend is running
   - Verify you see "Running on http://127.0.0.1:5000"
   - Look for error messages in output

2. **Frontend shows error?**
   - Open browser DevTools (F12)
   - Check Console tab for error messages
   - Verify backend is accessible at http://127.0.0.1:5000

3. **Analysis takes too long?**
   - First time analysis may be slow
   - Check backend terminal for processing messages
   - With API key, it uses Claude AI and may take 5-10 seconds

4. **Results don't include explanations?**
   - You likely don't have API key configured
   - Edit backend/.env with your Anthropic API key
   - Restart backend server

---

**All systems operational!** ✅ 

You can now analyze legal documents in real-time.
