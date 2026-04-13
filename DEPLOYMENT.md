# Legal Document Simplifier - Deployment Guide

## Local Development Setup

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

5. **Run backend**
   ```bash
   python app.py
   ```
   Server will start at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Start a local server** (if not using a framework)
   - Using Python: `python -m http.server 8000`
   - Using Node: `npx http-server`
   - Access at: `http://localhost:8000` or `http://localhost:3000`

### Test the Setup

1. **Test backend health**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Run test suite**
   ```bash
   cd backend
   python test_api.py
   ```

3. **Access frontend**
   Open browser to your frontend server URL

---

## Docker Deployment

### Build and Run with Docker

1. **Create Dockerfile for Backend**
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   ENV FLASK_APP=app.py
   ENV PYTHONUNBUFFERED=1

   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
   ```

2. **Build and run**
   ```bash
   docker build -t legal-simplifier-backend .
   docker run -e ANTHROPIC_API_KEY=your_key -p 5000:5000 legal-simplifier-backend
   ```

---

## Cloud Deployment

### Option 1: Heroku

1. **Install Heroku CLI**
   ```bash
   npm install -g heroku
   heroku login
   ```

2. **Create Procfile** in backend directory:
   ```
   web: gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app
   ```

3. **Create runtime.txt** in backend directory:
   ```
   python-3.11.7
   ```

4. **Deploy**
   ```bash
   cd backend
   heroku create legal-simplifier
   heroku config:set ANTHROPIC_API_KEY=your_key
   git push heroku main
   ```

### Option 2: AWS EC2

1. **Connect to EC2 instance**
   ```bash
   ssh -i your-key.pem ec2-user@your-instance.compute.amazonaws.com
   ```

2. **Install dependencies**
   ```bash
   sudo yum update
   sudo yum install python3 python3-pip postgresql
   ```

3. **Clone repository**
   ```bash
   git clone your-repo.git
   cd LegalDocSimplifier/backend
   ```

4. **Setup virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Configure environment**
   ```bash
   echo "ANTHROPIC_API_KEY=your_key" > .env
   ```

6. **Run with systemd**
   Create `/etc/systemd/system/legal-simplifier.service`:
   ```ini
   [Unit]
   Description=Legal Document Simplifier
   After=network.target

   [Service]
   User=ec2-user
   WorkingDirectory=/home/ec2-user/LegalDocSimplifier/backend
   Environment="PATH=/home/ec2-user/LegalDocSimplifier/backend/venv/bin"
   ExecStart=/home/ec2-user/LegalDocSimplifier/backend/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Start service:
   ```bash
   sudo systemctl start legal-simplifier
   sudo systemctl enable legal-simplifier
   ```

### Option 3: Google Cloud Run

1. **Create app.yaml**
   ```yaml
   runtime: python39
   
   env: standard
   
   env_variables:
     ANTHROPIC_API_KEY: "your_key"
   ```

2. **Deploy**
   ```bash
   gcloud app deploy
   ```

### Option 4: Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create fly.toml**
   ```toml
   app = "legal-simplifier"
   
   [build]
   builder = "paketobuildpacks/builder:base"
   
   [env]
   PYTHONUNBUFFERED = "true"
   
   [[services]]
   internal_port = 5000
   protocol = "tcp"
   
   [services.concurrency]
   hard_limit = 512
   soft_limit = 450
   ```

3. **Deploy**
   ```bash
   fly launch
   fly deploy
   fly secrets set ANTHROPIC_API_KEY=your_key
   ```

---

## Production Considerations

### 1. Environment Management
- Use strong, unique API keys
- Store secrets in environment variables, not in code
- Rotate API keys regularly

### 2. Database
- For production, use PostgreSQL instead of SQLite
- Enable automatic backups
- Use connection pooling
- Monitor query performance

### 3. Monitoring & Logging
- Set up application monitoring (Datadog, New Relic)
- Enable request logging
- Set up alerts for errors
- Monitor API usage and costs

### 4. Performance Optimization
```python
# Add caching for common clauses
from functools import lru_cache

@lru_cache(maxsize=1000)
def cache_clause_analysis(clause_text):
    # Cache results of expensive operations
    pass
```

### 5. Rate Limiting
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/simplify', methods=['POST'])
@limiter.limit("10 per minute")
def simplify_document():
    # Rate-limited endpoint
    pass
```

### 6. Security Headers
```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

### 7. HTTPS/TLS
- Always use HTTPS in production
- Use valid SSL certificates (Let's Encrypt is free)
- Enforce HTTPS redirects

### 8. API Documentation
- Document all endpoints with examples
- Provide status codes and error messages
- Use OpenAPI/Swagger format

---

## Monitoring Commands

### Check Logs (Production)
```bash
# Heroku
heroku logs --tail

# EC2 with systemd
sudo journalctl -u legal-simplifier -f

# Docker
docker logs -f container_name
```

### Monitor Resources
```bash
# Check database size
du -sh legal_documents.db

# Monitor CPU/Memory (EC2)
top
htop

# Check API response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/api/health
```

### Health Checks
```bash
# Basic health check
curl http://your-api.com/api/health

# Monitor endpoint performance
time curl -X POST http://your-api.com/api/simplify -H "Content-Type: application/json" -d '{"text": "sample"}'
```

---

## Scaling Strategies

### Horizontal Scaling
1. Load balancer (NGINX, HAProxy)
2. Multiple backend instances
3. Shared database
4. Session storage (Redis)

### Vertical Scaling
1. Larger machine instance
2. More CPU cores
3. More RAM
4. GPU for model inference

### Database Optimization
- Connection pooling
- Query optimization
- Caching layer (Redis)
- Database replication

---

## Cost Optimization

### API Costs
- Anthropic: ~$3-15 per 1M tokens
- Monitor token usage
- Implement caching to reduce API calls
- Consider batch processing

### Computing
- Use smaller instances for low traffic
- Auto-scale based on demand
- Use spot/preemptible instances
- Cache static assets

### Storage
- Archive old analyses
- Implement database cleanup jobs
- Use object storage (S3) for large files

---

## Troubleshooting Deployment

### Issue: 502 Bad Gateway
Check backend logs and ensure service is running

### Issue: High latency
- Check database query performance
- Implement caching
- Scale horizontally
- Monitor API rate limits

### Issue: Out of memory
- Reduce batch size
- Implement chunking for large documents
- Monitor model memory usage
- Use GPU acceleration

### Issue: Database connection errors
- Check connection string
- Verify database is running
- Check firewall rules
- Implement connection pooling

---

## Backup & Recovery

### Database Backups
```bash
# PostgreSQL daily backup
pg_dump legal_documents_db > backup_$(date +%Y%m%d).sql

# Restore from backup
psql legal_documents_db < backup_20240115.sql
```

### Application Recovery
- Keep deployment scripts
- Version all configurations
- Document rollback procedures
- Test disaster recovery regularly
