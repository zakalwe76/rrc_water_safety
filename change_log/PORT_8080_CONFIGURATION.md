# Port Configuration Change - 8080 for Fly.io Compatibility

## Change Summary

Updated application port configuration from 5000 to 8080 to ensure compatibility with Fly.io deployment platform.

## Problem

Fly.io expects applications to run on port 8080 internally. The application was previously configured to run on port 5000, which would cause deployment issues on Fly.io.

## Solution

Changed all port references from 5000 to 8080 while maintaining local development accessibility via port mapping.

## Files Modified

### 1. Dockerfile
**Changed:**
- `EXPOSE 5000` → `EXPOSE 8080`
- `gunicorn --bind 0.0.0.0:5000` → `gunicorn --bind 0.0.0.0:8080`

**New configuration:**
```dockerfile
# Expose port
EXPOSE 8080

# Run the application with gunicorn (single worker to maintain cache consistency)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "--log-level", "info", "app:app"]
```

### 2. docker-compose.yml
**Changed:**
- Port mapping from `"5000:5000"` → `"5000:8080"`

**New configuration:**
```yaml
services:
  web:
    build: .
    ports:
      - "5000:8080"  # Map local 5000 to container 8080 (Fly.io uses 8080)
    environment:
      - FLASK_ENV=production
      - DEMO_MODE=false
    restart: unless-stopped
```

**Explanation:**
- Maps local port 5000 to container port 8080
- Developers can still access via `http://localhost:5000`
- Container runs on 8080 internally (Fly.io compatible)

### 3. fly.toml
**Status:** Already configured correctly with `internal_port = 8080`

No changes needed - file was already set up for port 8080.

## Port Configuration Summary

### Local Development
- **Access URL**: `http://localhost:5000`
- **Container internal port**: 8080
- **Port mapping**: Host 5000 → Container 8080
- **Why**: Familiar port for developers, no disruption to local workflow

### Fly.io Production
- **Container internal port**: 8080 (required by Fly.io)
- **External access**: Automatic via Fly.io proxy (HTTPS)
- **Configuration**: `internal_port = 8080` in fly.toml

### Port Flow Diagram

```
Local Development:
Browser (localhost:5000) 
    ↓ [docker port mapping]
Container (0.0.0.0:8080)
    ↓ [gunicorn]
Flask App

Fly.io Production:
Internet (your-app.fly.dev)
    ↓ [Fly.io proxy/HTTPS]
Container (0.0.0.0:8080)
    ↓ [gunicorn]
Flask App
```

## Testing Performed

✅ **Local Docker**: Confirmed app accessible at `http://localhost:5000`
✅ **Container Logs**: Verified gunicorn listening on `0.0.0.0:8080`
✅ **Port Mapping**: Docker correctly maps 5000→8080
✅ **Fly.io Config**: Confirmed fly.toml has `internal_port = 8080`
✅ **Application Functionality**: All features work correctly

## Why Port 8080?

### Fly.io Requirements
- Fly.io expects applications to bind to port 8080 by default
- The platform routes external traffic to this internal port
- Using a different port requires additional configuration

### Industry Standard
- Port 8080 is a common alternative HTTP port
- Often used for application servers (vs 80 for web servers)
- Widely recognized and firewall-friendly

### Benefits
- **Zero configuration** on Fly.io
- **Standard practice** for containerized apps
- **No conflicts** with system ports (< 1024)

## Backward Compatibility

### Local Development
- ✅ No change - still accessible via `localhost:5000`
- ✅ Docker Compose handles port mapping automatically
- ✅ Developers don't need to change their workflow

### Deployment
- ✅ Fly.io deployment will work correctly
- ✅ GitHub Actions deployment unchanged
- ✅ No environment variable changes needed

## Related Configuration Files

### Unchanged Files
- **app.py**: Port 5000 reference only for Flask dev server (not used in production)
- **.github/workflows/fly-deploy.yml**: No changes needed
- **requirements.txt**: No changes needed

### Configuration Consistency

| File | Port Setting | Purpose |
|------|-------------|---------|
| Dockerfile | 8080 | Container internal port |
| docker-compose.yml | 5000:8080 | Local dev port mapping |
| fly.toml | 8080 | Fly.io internal port |
| app.py | 5000 | Flask dev server only (not used) |

## Deployment Instructions

### Local Testing
```bash
# Build and run
docker-compose up -d --build

# Access application
open http://localhost:5000

# Verify container port
docker-compose logs web | grep "Listening"
# Should show: Listening at: http://0.0.0.0:8080
```

### Fly.io Deployment
```bash
# No changes needed - will automatically use port 8080
flyctl deploy

# Or via GitHub Actions (automatic on push)
git push origin main
```

## Troubleshooting

### Issue: Can't access locally
**Symptom**: `http://localhost:5000` doesn't work

**Check**:
```bash
docker-compose ps
# Verify: 0.0.0.0:5000->8080/tcp
```

**Fix**: Ensure port mapping is `"5000:8080"` in docker-compose.yml

### Issue: Fly.io deployment fails
**Symptom**: Application doesn't start on Fly.io

**Check**:
```bash
flyctl logs
# Look for port binding errors
```

**Fix**: Ensure Dockerfile uses port 8080 and fly.toml has `internal_port = 8080`

### Issue: Connection refused
**Symptom**: Container starts but can't connect

**Check**:
```bash
docker exec -it rrc_water_safety-web-1 sh
netstat -tlnp | grep 8080
```

**Fix**: Verify gunicorn binds to `0.0.0.0:8080` (not `127.0.0.1`)

## Future Considerations

### If Port Needs to Change
To use a different port in the future:

1. Update Dockerfile: `EXPOSE <PORT>` and gunicorn bind
2. Update fly.toml: `internal_port = <PORT>`
3. Update docker-compose.yml: `"5000:<PORT>"`
4. Test locally before deploying

### Multi-Environment Support
For different ports per environment, consider:
- Environment variables: `PORT=${PORT:-8080}`
- Separate docker-compose files: `docker-compose.prod.yml`
- Configuration management: Config files per environment

## Security Notes

- Port 8080 is non-privileged (> 1024) - no root needed
- Fly.io handles external HTTPS automatically
- Local development uses HTTP (acceptable for localhost)
- No sensitive services should bind to 8080 during development

## References

- **Fly.io Docs**: https://fly.io/docs/reference/configuration/#services-ports
- **Docker Port Mapping**: https://docs.docker.com/config/containers/container-networking/
- **Gunicorn Binding**: https://docs.gunicorn.org/en/stable/settings.html#bind

---

**Change Status**: ✅ **COMPLETE**  
**Tested**: ✅ **PASSED**  
**Ready for Deployment**: ✅ **YES**  
**Date**: February 27, 2026  
**Reason**: Fly.io compatibility
