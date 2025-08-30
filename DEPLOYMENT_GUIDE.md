# SWMS MCP Server Deployment Guide

## 🚀 Deployment Options

### Option 1: FastMCP Cloud (Recommended)

FastMCP Cloud provides the easiest deployment with automatic scaling and monitoring.

#### Prerequisites
- GitHub account
- FastMCP Cloud account ([sign up here](https://fastmcp.cloud))
- Gemini API key

#### Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy SWMS MCP Server"
   git push origin main
   ```

2. **Connect to FastMCP Cloud**
   - Go to [FastMCP Cloud Dashboard](https://fastmcp.cloud)
   - Click "New Server"
   - Select "Import from GitHub"
   - Authorize and select your repository

3. **Configure Environment Variables**
   - In the deployment settings, add:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     R2_PUBLIC_URL=https://pub-bb6a39bd73444f4582d3208b2257c357.r2.dev
     ```

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete (usually 1-2 minutes)
   - Copy your server URL

5. **Test Deployment**
   ```bash
   # Test with FastMCP CLI
   fastmcp test https://your-server.fastmcp.cloud
   ```

### Option 2: Local Development Server

Perfect for testing and development.

#### Prerequisites
- Python 3.11+
- pip or uv package manager

#### Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/jezweb/swims-mcp-server.git
   cd swims-mcp-server
   ```

2. **Install Dependencies**
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Using uv (faster)
   uv pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit and add your GEMINI_API_KEY
   ```

4. **Run Server**
   ```bash
   # Development mode (with auto-reload)
   fastmcp dev server.py
   
   # Production mode
   fastmcp run server.py
   ```

5. **Verify Server**
   ```bash
   # Check server status
   curl http://localhost:8000/status
   ```

### Option 3: Docker Container

Deploy as a containerized service.

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run server
CMD ["fastmcp", "run", "server.py", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build and Run
```bash
# Build image
docker build -t swms-mcp-server .

# Run container
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key_here \
  -e R2_PUBLIC_URL=https://pub-bb6a39bd73444f4582d3208b2257c357.r2.dev \
  --name swms-server \
  swms-mcp-server
```

### Option 4: Cloud Platform Deployment

#### Google Cloud Run
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/swms-mcp-server

# Deploy to Cloud Run
gcloud run deploy swms-mcp-server \
  --image gcr.io/PROJECT_ID/swms-mcp-server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key_here
```

#### AWS Lambda (with FastAPI adapter)
```bash
# Install serverless framework
npm install -g serverless

# Deploy
serverless deploy --stage prod
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | - | Your Gemini API key |
| `GOOGLE_API_KEY` | 🔄 Alternative | - | Alternative to GEMINI_API_KEY |
| `R2_PUBLIC_URL` | ❌ No | See below | R2 bucket public URL |

Default R2 URL: `https://pub-bb6a39bd73444f4582d3208b2257c357.r2.dev`

### API Key Setup

1. **Get Gemini API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Click "Create API Key"
   - Copy the key

2. **Set Environment Variable**
   ```bash
   # Linux/Mac
   export GEMINI_API_KEY="your_key_here"
   
   # Windows
   set GEMINI_API_KEY=your_key_here
   ```

### R2 Document Storage

The server uses pre-configured R2 storage with regulatory documents. No additional setup required.

#### Available Documents
- ✅ 25 PDF documents across all jurisdictions
- ✅ National Safe Work Australia guidelines
- ✅ State-specific codes of practice
- ✅ SWMS templates and examples

## 🔍 Testing Your Deployment

### 1. Server Health Check
```python
import asyncio
from server import get_server_status

async def test_health():
    result = await get_server_status()
    print(result)

asyncio.run(test_health())
```

### 2. Upload and Analyze Test
```python
async def test_analysis():
    # Upload from URL
    upload = await upload_swms_from_url({
        "url": "https://example.com/test-swms.pdf"
    })
    
    # Analyze for NSW compliance
    analysis = await analyze_swms_compliance({
        "document_id": upload["document_id"],
        "jurisdiction": "nsw"
    })
    
    print(analysis["overall_assessment"])

asyncio.run(test_analysis())
```

### 3. MCP Client Test
```bash
# Using FastMCP client
fastmcp client connect http://localhost:8000

# List available tools
> list_tools

# Test server status
> call get_server_status
```

## 📊 Monitoring

### Logging
```python
# Configure logging in server.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Health Endpoints
- `/health` - Basic health check
- `/status` - Detailed server status
- `/metrics` - Performance metrics (if enabled)

## 🔒 Security Considerations

### API Key Security
- ⚠️ Never commit API keys to version control
- ✅ Use environment variables or secrets management
- ✅ Rotate keys regularly
- ✅ Use different keys for dev/staging/production

### Network Security
- Configure CORS if needed
- Use HTTPS in production
- Implement rate limiting for public endpoints

### Example CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_methods=["POST"],
    allow_headers=["*"],
)
```

## 🚨 Troubleshooting

### Common Issues

#### 1. API Key Not Working
```bash
# Check if key is set
echo $GEMINI_API_KEY

# Test API key directly
curl -H "x-goog-api-key: YOUR_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models
```

#### 2. R2 Documents Not Loading
- Check R2 public URL is accessible
- Verify network connectivity
- Check server logs for fetch errors

#### 3. Memory Issues with Large Documents
```bash
# Increase memory limit
export PYTHON_MAX_MEMORY=4G
```

#### 4. Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
fastmcp dev server.py --debug
```

## 📈 Performance Optimization

### Caching Strategy
- Gemini file uploads cached for 24 hours
- Local file cache at `/tmp/swms-file-cache/`
- R2 documents cached after first fetch

### Scaling Recommendations
- Use connection pooling for high load
- Implement request queuing for Gemini API
- Consider edge caching for R2 documents

## 🔄 Updates and Maintenance

### Updating the Server
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart server
fastmcp restart
```

### Database Migrations
Not applicable - server is stateless and uses external storage.

## 📞 Support

### Getting Help
- 📖 [API Documentation](./API_DOCUMENTATION.md)
- 🐛 [Report Issues](https://github.com/jezweb/swims-mcp-server/issues)
- 💬 [Discussions](https://github.com/jezweb/swims-mcp-server/discussions)

### Logs Location
- Local: `./logs/` (if configured)
- Docker: `docker logs swms-server`
- Cloud Run: Google Cloud Console Logs
- FastMCP Cloud: Dashboard logs viewer

## 🎯 Quick Start Checklist

- [ ] Obtain Gemini API key
- [ ] Choose deployment method
- [ ] Set environment variables
- [ ] Deploy server
- [ ] Test with health check
- [ ] Verify R2 document access
- [ ] Test SWMS upload and analysis
- [ ] Configure monitoring (optional)
- [ ] Set up backups (if needed)

---

For more details, see the [README](./README.md) and [API Documentation](./API_DOCUMENTATION.md).