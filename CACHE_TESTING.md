# Cache Testing Guide

## Quick Test: Verify Cache is Working

### Test 1: Cache Persistence (data should NOT change immediately)

```bash
# Get current data
curl http://localhost:5000/api/conditions

# Wait 5 seconds
sleep 5

# Get data again - should be SAME (from cache)
curl http://localhost:5000/api/conditions

# Check logs - should say "cache is still valid"
docker-compose logs --tail=10 web
```

**Expected:** Same river_flow value, cache age increases

### Test 2: Force Refresh (manual override)

```bash
# Force refresh
curl "http://localhost:5000/api/conditions?force=true"

# Check logs - should say "Force refresh requested"
docker-compose logs --tail=10 web
```

**Expected:** Fresh data fetched, cache age = 0

### Test 3: Cache Expiry (after 15 minutes)

**Option A: Wait 15 minutes**
```bash
# Initial request
curl http://localhost:5000/api/conditions | grep river_flow

# Wait 16 minutes
sleep 960

# Request again - should fetch fresh data
curl http://localhost:5000/api/conditions | grep river_flow

# Check logs
docker-compose logs --tail=20 web | grep "cache age"
```

**Expected:** See "River cache age: 16.0 minutes" then "fetching fresh data"

**Option B: Test with shorter expiry (for quick verification)**

1. Edit `app.py` line 26:
   ```python
   CACHE_EXPIRY_MINUTES = 0.5  # 30 seconds for testing
   ```

2. Rebuild:
   ```bash
   docker-compose up -d --build
   ```

3. Test:
   ```bash
   # Initial request
   curl http://localhost:5000/api/conditions
   
   # Wait 35 seconds
   sleep 35
   
   # Request again
   curl http://localhost:5000/api/conditions
   
   # Check logs
   docker-compose logs --tail=20 web
   ```

4. **Remember to change back to 15 minutes!**

### Test 4: UI "Refresh Now" Button

1. Open http://localhost:5000 in browser
2. Note the values and cache age
3. Click "Refresh Now"
4. Observe:
   - Button changes to "Refreshing..."
   - Cache age resets to 0
   - New data may appear (if sources updated)
5. Check browser console and logs

### Verify Logs Show Everything

Good logs should show:
```
INFO:app:River cache age: X.X minutes
INFO:app:River cache is still valid    [if < 15 min]
-- OR --
INFO:app:River cache expired - fetching fresh data    [if > 15 min]
INFO:app:Fetching river data from...
INFO:app:Successfully fetched river data: flow=XXX m³/s
```

## Monitoring Cache in Production

### View logs in real-time
```bash
docker-compose logs -f web
```

### Check cache age via API
```bash
curl -s http://localhost:5000/api/conditions | python -m json.tool | grep cache_age -A 3
```

### Monitor data updates
```bash
# Save current flow
echo $(curl -s http://localhost:5000/api/conditions | python -m json.tool | grep river_flow)

# Check again later
echo $(curl -s http://localhost:5000/api/conditions | python -m json.tool | grep river_flow)
```

## Troubleshooting

### Cache seems stuck
```bash
# Force refresh
curl "http://localhost:5000/api/conditions?force=true"

# Or restart container
docker-compose restart
```

### Want to see all cache activity
```bash
# Full logs
docker-compose logs web | grep -i cache

# Or follow live
docker-compose logs -f web | grep -i cache
```

### Data not updating after 15 minutes
1. Check logs for errors
2. Verify external APIs are accessible
3. Confirm cache_age is actually > 900 seconds
4. Try force refresh to test connectivity

## Normal Operation Indicators

✅ First request after startup: "cache is empty" → fetches data
✅ Requests within 15 min: "cache is still valid" → uses cache
✅ Requests after 15 min: "cache expired" → fetches fresh data
✅ Force refresh: "clearing cache" → fetches fresh data
✅ Cache age displays correctly in UI (0-900 seconds)

---

**All tests passing means cache is working perfectly!** 🎉
