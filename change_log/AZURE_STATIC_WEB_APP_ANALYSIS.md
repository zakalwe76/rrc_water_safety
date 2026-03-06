# Azure Static Web App Feasibility Analysis

## Executive Summary

**Can it be done?** ✅ **Yes, but with significant refactoring**

**Effort Level:** 🟡 **Medium-High** (Major architectural changes required)

**Recommendation:** 🟠 **Not recommended unless Azure is a hard requirement**

---

## Current Architecture vs Azure Static Web Apps

### Current Architecture

```
┌─────────────────────────────────────┐
│     Docker Container (Continuous)    │
├─────────────────────────────────────┤
│  Gunicorn (WSGI Server)             │
│  ├─ Flask Application (Python)      │
│  ├─ Jinja2 Templates (Server-side)  │
│  ├─ In-Memory Cache (15 min)        │
│  ├─ External API Calls              │
│  └─ Business Logic                  │
└─────────────────────────────────────┘
         ↓ (Always running)
    HTTP Requests → Responses
```

**Characteristics:**
- Stateful (in-memory cache)
- Server-side rendering
- Continuous operation
- Single process handles everything
- Cache shared across requests

### Azure Static Web Apps Architecture

```
┌──────────────────────────┐
│   Static Assets (CDN)    │
│   ├─ HTML               │
│   ├─ CSS                │
│   └─ JavaScript         │
└──────────────────────────┘
         ↓
    Browser renders
         ↓ (API calls)
┌──────────────────────────┐
│  Azure Functions (API)   │
│  ├─ Python Functions     │
│  ├─ Stateless execution  │
│  ├─ Cold starts          │
│  └─ External cache needed│
└──────────────────────────┘
```

**Characteristics:**
- Stateless (no in-memory cache)
- Client-side rendering
- Functions spin up per request
- Separate concerns (frontend/backend)
- Cache requires external service

---

## Required Changes

### 1. Architecture Split

**Current:** Monolithic Flask app with server-side rendering

**Needed:** Separate static frontend + serverless API

```
Before:
flask_app/
├── app.py (routes + logic + rendering)
├── templates/ (Jinja2)
└── static/ (CSS/JS)

After:
azure_static_web_app/
├── frontend/
│   ├── index.html (standalone)
│   ├── css/
│   └── js/
│       └── app.js (client-side logic)
└── api/
    ├── get_conditions/
    │   └── __init__.py (Azure Function)
    ├── requirements.txt
    └── host.json
```

### 2. Template Conversion

**Current:** Jinja2 server-side templates
```python
# Flask renders HTML server-side
@app.route('/')
def index():
    return render_template('index.html')
```

**Needed:** Static HTML + JavaScript
```html
<!-- Static HTML served from CDN -->
<!DOCTYPE html>
<html>
<body>
    <div id="app"></div>
    <script src="app.js"></script>
</body>
</html>
```

```javascript
// app.js - Client-side rendering
fetch('/api/conditions')
    .then(res => res.json())
    .then(data => renderUI(data));
```

**Changes Required:**
- Convert Jinja2 templates to static HTML
- Move all dynamic content generation to JavaScript
- Implement client-side templating (or use framework)
- Handle data binding in browser
- Update all styling references

**Effort:** 4-6 hours

### 3. Caching Strategy Overhaul

**Current:** In-memory cache (simple, fast, effective)
```python
cache = {
    'river_data': None,
    'river_timestamp': None,
    'weather_data': None,
    'weather_timestamp': None
}
```

**Problem:** Azure Functions are stateless
- Each function invocation is independent
- No shared memory between calls
- Cache would reset on every request
- Cold starts lose all state

**Solution Options:**

#### Option A: Azure Table Storage (Recommended)
```python
from azure.data.tables import TableServiceClient

def get_cached_data(key):
    table_client = TableServiceClient.from_connection_string(conn_str)
    table = table_client.get_table_client("cache")
    entity = table.get_entity(partition_key="cache", row_key=key)
    
    # Check if expired
    if is_expired(entity['timestamp']):
        return None
    return entity['data']
```

**Pros:**
- Serverless-native
- Simple to implement
- Free tier available (25k operations/month)
- Low latency

**Cons:**
- Adds external dependency
- Need connection string management
- Slightly slower than in-memory

**Cost:** Free tier sufficient

#### Option B: Azure Redis Cache
```python
import redis

r = redis.Redis(
    host='your-cache.redis.cache.windows.net',
    port=6380,
    password='your-password',
    ssl=True
)

def get_cached_data(key):
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    return None
```

**Pros:**
- Fastest external cache
- Redis features (TTL, etc.)
- Familiar technology

**Cons:**
- Costs money (~$15-20/month minimum)
- Overkill for this use case
- More complex setup

**Cost:** $15-20/month

#### Option C: No Cache (Simplest)
```python
# Just fetch data on every request
def get_conditions():
    river_data = fetch_river_data()
    weather_data = fetch_weather_data()
    return calculate_conditions(river_data, weather_data)
```

**Pros:**
- Simplest implementation
- No cache management
- Always fresh data

**Cons:**
- Slower response times (300-500ms)
- More API calls to external sources
- Higher latency for users
- May hit rate limits

**Cost:** Free

**Recommendation:** Option A (Azure Table Storage)
- Good balance of simplicity and performance
- Free tier sufficient
- Serverless-native solution

**Effort:** 6-8 hours (including testing)

### 4. Flask Routes → Azure Functions

**Current:** Flask routes
```python
@app.route('/api/conditions')
def get_conditions():
    update_cache_if_needed()
    # ... logic ...
    return jsonify(result)
```

**Needed:** Azure Functions
```python
# api/get_conditions/__init__.py
import azure.functions as func
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Conditions request received')
    
    # Fetch from cache (Azure Table Storage)
    cached = get_from_cache('conditions')
    if cached and not is_expired(cached):
        return func.HttpResponse(
            body=json.dumps(cached),
            mimetype="application/json"
        )
    
    # Fetch fresh data
    river_data = fetch_river_data()
    weather_data = fetch_weather_data()
    conditions = calculate_conditions(river_data, weather_data)
    
    # Store in cache
    save_to_cache('conditions', conditions)
    
    return func.HttpResponse(
        body=json.dumps(conditions),
        mimetype="application/json"
    )
```

**Additional Files Needed:**
```json
// api/get_conditions/function.json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["get"],
      "route": "conditions"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

**Changes Required:**
- Rewrite each Flask route as separate Azure Function
- Update function signatures
- Add Azure Functions configuration
- Handle CORS properly
- Update error handling
- Adapt logging

**Effort:** 8-10 hours

### 5. External API Integration

**Current:** Direct HTTP calls with requests library
```python
response = requests.get(RIVER_API_URL, timeout=10)
```

**Needed:** Same, but with Azure-specific considerations

**Challenges:**
- **Cold starts:** First request takes 2-5 seconds (function initialization)
- **Timeout limits:** Azure Functions free tier: 5 minutes max execution
- **Retry logic:** May need to handle cold start retries
- **Connection pooling:** Doesn't persist across invocations

**Required Changes:**
```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_http_session():
    """Create session with retry logic for cold starts"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def fetch_river_data():
    session = get_http_session()
    try:
        response = session.get(RIVER_API_URL, timeout=30)
        return response.json()
    except requests.Timeout:
        logging.error("River API timeout")
        return None
```

**Effort:** 2-3 hours

### 6. Configuration & Secrets

**Current:** Environment variables in docker-compose
```yaml
environment:
  - DEMO_MODE=false
```

**Needed:** Azure App Settings + Key Vault

```bash
# Via Azure Portal or CLI
az functionapp config appsettings set \
    --name your-app \
    --resource-group your-rg \
    --settings "DEMO_MODE=false"
```

**For sensitive data (if needed):**
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
secret = client.get_secret("api-key")
```

**Effort:** 2-3 hours

### 7. Deployment Configuration

**Current:** Dockerfile + docker-compose + GitHub Actions (Fly.io)

**Needed:** Azure Static Web App config + GitHub Actions (Azure)

```yaml
# staticwebapp.config.json
{
  "routes": [
    {
      "route": "/api/*",
      "allowedRoles": ["anonymous"]
    }
  ],
  "navigationFallback": {
    "rewrite": "/index.html"
  },
  "responseOverrides": {
    "404": {
      "rewrite": "/index.html"
    }
  }
}
```

```yaml
# .github/workflows/azure-static-web-apps.yml
name: Azure Static Web Apps CI/CD

on:
  push:
    branches:
      - main

jobs:
  build_and_deploy_job:
    runs-on: ubuntu-latest
    name: Build and Deploy
    steps:
      - uses: actions/checkout@v3
      
      - name: Build And Deploy
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "/frontend"
          api_location: "/api"
          output_location: ""
```

**Effort:** 3-4 hours

---

## Limitations & Challenges

### 1. Cold Starts ❄️

**Problem:** Azure Functions in free/consumption tier have cold starts

**Impact:**
- First request after inactivity: 2-5 seconds
- Affects user experience
- More noticeable than current Fly.io deployment

**Mitigation:**
- Accept cold starts (free tier limitation)
- Use Premium plan ($15-20/month) for "always warm"
- Implement loading indicators in UI
- Pre-warm functions with scheduled pings (limited effectiveness)

### 2. Stateless Architecture

**Problem:** No persistent in-memory state

**Impact:**
- Must use external cache (Table Storage/Redis)
- Additional complexity
- Slightly higher latency
- More moving parts

**Current:** Cache hit in ~1ms (in-memory)
**Azure:** Cache hit in ~10-20ms (Table Storage)

### 3. Execution Time Limits

**Problem:** Azure Functions timeout

**Limits:**
- Consumption plan: 5 minutes (configurable, 10 min max)
- Should be fine for your use case (API calls take <10 seconds)

**Risk:** Low for this application

### 4. CORS Configuration

**Problem:** Static site + separate API domain = CORS issues

**Solution Required:**
```python
def main(req: func.HttpRequest) -> func.HttpResponse:
    # ... logic ...
    
    response = func.HttpResponse(
        body=json.dumps(result),
        mimetype="application/json"
    )
    
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    return response
```

**Effort:** 1-2 hours

### 5. Development Experience

**Current:**
```bash
docker-compose up
# Immediate: http://localhost:5000
# Edit code → Auto-reload
```

**Azure Static Web Apps:**
```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Install Static Web Apps CLI
npm install -g @azure/static-web-apps-cli

# Start local emulator
swa start frontend --api-location api

# More complex setup
# Separate terminal for functions
# Less seamless hot-reload
```

**Impact:** Slower development cycle

### 6. Monitoring & Debugging

**Current:**
```bash
docker-compose logs -f web
# Simple, straightforward
```

**Azure:**
- Application Insights (required for good monitoring)
- Azure Portal logs (web interface)
- CLI: `az functionapp logs tail`
- More complex log aggregation

**Impact:** Steeper learning curve

---

## Cost Comparison

### Current (Fly.io) - FREE

```
Free Tier:
- 3 shared VMs (256MB each)
- 160GB bandwidth/month
- No cold starts
- Always on

Cost: $0/month
```

### Azure Static Web Apps

#### Option 1: Free Tier (with limitations)
```
Included:
- Static hosting (CDN)
- Azure Functions (1M executions/month)
- 100GB bandwidth/month
- Cold starts (yes)

Additional Costs:
- Azure Table Storage: FREE (25k ops/month sufficient)

Total: $0/month
```

**Limitations:**
- Cold starts on Functions
- Limited executions (should be fine)
- No custom domains on free tier
- Basic features only

#### Option 2: Standard Tier (better experience)
```
Standard Tier: $9/month
- No cold starts
- Custom domains
- Better performance
- SLA included

Additional:
- Table Storage: FREE
or
- Redis Cache: $15-20/month (optional)

Total: $9-29/month
```

### Verdict on Cost

**Current:** FREE, no cold starts, excellent performance
**Azure Free:** FREE, but cold starts, more complex
**Azure Paid:** $9-29/month for similar experience to current free Fly.io

---

## Effort Estimation

### Development Time

| Task | Hours | Complexity |
|------|-------|------------|
| Template → Static HTML/JS | 4-6 | Medium |
| Cache → Azure Table Storage | 6-8 | Medium-High |
| Flask Routes → Functions | 8-10 | Medium |
| External API adjustments | 2-3 | Low-Medium |
| Configuration & secrets | 2-3 | Medium |
| Deployment setup | 3-4 | Medium |
| Testing & debugging | 4-6 | Medium |
| Documentation updates | 2-3 | Low |
| **TOTAL** | **31-43 hours** | **Medium-High** |

### Additional Considerations
- Learning Azure specifics: +5-10 hours
- Troubleshooting unforeseen issues: +5-10 hours
- **Realistic Total: 40-60 hours** (~1-2 weeks full-time)

---

## Pros & Cons Analysis

### ✅ Pros of Azure Static Web Apps

1. **Azure Ecosystem Integration**
   - Seamless with other Azure services
   - Good if already using Azure
   - Enterprise authentication (Azure AD)

2. **Scalability**
   - Auto-scales to demand
   - No manual scaling needed
   - CDN distribution

3. **Separation of Concerns**
   - Clear frontend/backend split
   - Independent scaling
   - Easier to hand off to separate teams

4. **CI/CD Integration**
   - GitHub Actions built-in
   - Preview environments per PR
   - Easy rollbacks

### ❌ Cons of Azure Static Web Apps

1. **Cold Starts**
   - 2-5 second delay after inactivity
   - Poor user experience on free tier
   - Costs money to eliminate

2. **Increased Complexity**
   - More moving parts
   - External cache required
   - More difficult debugging
   - Steeper learning curve

3. **Loss of Simplicity**
   - Current Docker setup is simple
   - Azure requires more services
   - More configuration needed
   - More can go wrong

4. **Development Experience**
   - Slower local development
   - More tools required
   - More complex setup
   - Less seamless hot-reload

5. **Cost**
   - Free tier has limitations
   - Good experience costs $9-29/month
   - Current Fly.io is free with no limitations

6. **Feature Loss**
   - In-memory caching speed
   - Always-on reliability
   - Simple deployment
   - Single container simplicity

---

## Alternative: Azure Container Instances

If you want to use Azure, **don't** refactor to Static Web Apps. Instead use **Azure Container Instances** with your existing Docker setup.

### Azure Container Instances

**Approach:** Deploy your current Docker container to Azure

**Advantages:**
- ✅ No code changes required
- ✅ Keep current architecture
- ✅ Keep in-memory caching
- ✅ No cold starts
- ✅ Simple deployment

**Setup:**
```bash
# Login to Azure
az login

# Create resource group
az group create --name rrc-water-safety --location eastus

# Deploy container
az container create \
  --resource-group rrc-water-safety \
  --name rrc-water-safety \
  --image your-docker-image \
  --dns-name-label rrc-water-safety \
  --ports 8080 \
  --environment-variables DEMO_MODE=false

# Access: http://rrc-water-safety.eastus.azurecontainer.io:8080
```

**Cost:** ~$10-15/month (0.5 vCPU, 1GB RAM)

**Effort:** 2-4 hours (just deployment, no refactoring)

---

## Recommendation

### 🔴 Do NOT Refactor to Azure Static Web Apps

**Reasons:**
1. **Not Worth the Effort:** 40-60 hours of work for no functional gain
2. **Worse User Experience:** Cold starts on free tier
3. **More Expensive:** Good experience costs $9-29/month vs current $0
4. **Increased Complexity:** More services, more configuration, more to manage
5. **Current Solution is Excellent:** Fly.io works perfectly, costs nothing

### ✅ Better Alternatives

#### Option 1: Stay on Fly.io (RECOMMENDED)
- **Cost:** FREE
- **Effort:** 0 hours
- **Experience:** Excellent (no cold starts)
- **Simplicity:** Single container
- **Reliability:** Proven working

#### Option 2: Azure Container Instances
- **Cost:** ~$10-15/month
- **Effort:** 2-4 hours
- **Experience:** Excellent (no cold starts)
- **Simplicity:** Same Docker container
- **Use if:** Azure is organizationally required

#### Option 3: Azure Static Web Apps
- **Cost:** $0 (with cold starts) or $9-29/month (without)
- **Effort:** 40-60 hours
- **Experience:** Fair (cold starts) or Good (paid tier)
- **Simplicity:** Complex (multiple services)
- **Use if:** Learning Azure or architectural reasons

---

## When Would Azure Static Web Apps Make Sense?

Azure Static Web Apps would be appropriate if:

1. ✅ **Organization requires Azure** (compliance, existing infrastructure)
2. ✅ **Need Azure AD integration** (enterprise authentication)
3. ✅ **Building a larger application** (multiple microservices)
4. ✅ **Team already experienced with Azure** (no learning curve)
5. ✅ **Budget for Standard tier** ($9/month acceptable)
6. ✅ **Want to learn Azure** (educational purpose)

For Reading Rowing Club's water safety app:
- ❌ No organizational requirement
- ❌ No authentication needed
- ❌ Simple single-purpose app
- ❌ Current solution works perfectly
- ❌ Free is important
- ❌ Simplicity is valuable

**Verdict:** NOT recommended for this project

---

## Summary

### Can it be done?
✅ **Yes**, technically feasible

### Should it be done?
🔴 **No**, not recommended

### Why not?
- Significant effort (40-60 hours)
- Worse free tier experience (cold starts)
- Costs money for good experience
- Increased complexity
- No functional benefits
- Current solution is excellent

### What to do instead?
Stay on Fly.io (free, fast, simple, working)

### If Azure is required?
Use Azure Container Instances (minimal changes, no refactoring)

---

**Analysis Date:** March 4, 2026  
**Status:** Feasible but not recommended  
**Effort:** 40-60 hours  
**Cost:** $0-29/month depending on tier  
**Recommendation:** ❌ Do not pursue unless Azure is organizationally required
