# Reading Rowing Club Water Safety App - Enhanced Specification

## Functional Specifications

### Startup Behavior
On starting up, the app should do the following things:

1. Connect to the UK Environment Agency's flood monitoring API at http://environment.data.gov.uk/flood-monitoring/id/measures/2200TH-flow--Mean-15_min-m3_s and retrieve all "items" listed in the json output and cache the results.

2. Read the data from the University of Reading's METFiDAS weather observations page at https://www.met.reading.ac.uk/weatherdata/Reading_AWS_weather_report.html and cache the values for "Air temperature: ºC", "10-metre maximum 3-sec wind gust: m/s", and the date and timestamp of the observation listed at the top of the page.

### Page View Behavior
When the page is viewed, the app should do the following:

1. Check the age of the cached data from the UK Environment Agency's flood monitoring API and the cached data from the University of Reading's METFiDAS weather observations page. If the cached data are older than 15 minutes, clear the cached data and retrieve fresh copies.

2. Calculate the rowing conditions for the boat categories "Fours, Quads, Eights" and "Singles, Doubles, Pairs" based on the rules specified in file called "rules.md" and then display the overall conditions for the boat categories as well as the individual conditions and values for "River Flow", "Wind Speed", and "Air Temperature".

### User Interaction Requirements

3. Provide a manual "Refresh Now" button that forces immediate fresh data retrieval from both external sources, bypassing the cache regardless of age.

4. Display cache age information to users so they can see data freshness.

5. Automatically refresh the displayed data periodically (recommended: every 5 minutes) to check if the backend cache needs updating.

### Data Source Transparency

6. Display the data sources with clickable links:
   - **River Flow**: Link to the Environment Agency API endpoint
     - URL: http://environment.data.gov.uk/flood-monitoring/id/measures/2200TH-flow--Mean-15_min-m3_s
     - Display: "Environment Agency" (clickable link) followed by the reading timestamp
   
   - **Weather Data**: Link to the University of Reading weather page
     - URL: https://www.met.reading.ac.uk/weatherdata/Reading_AWS_weather_report.html
     - Display: "University of Reading" (clickable link) followed by the observation timestamp
   
   - Links should open in a new tab/window (use `target="_blank"` and `rel="noopener noreferrer"` for security)
   - Style links to be visually distinct (e.g., colored, underlined on hover)

---

## Technical Implementation Notes

### Environment Agency API Structure

The Environment Agency API returns JSON with the following structure:

```json
{
  "@context": "http://environment.data.gov.uk/flood-monitoring/meta/context.jsonld",
  "meta": {
    "publisher": "Environment Agency",
    "licence": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
    "documentation": "http://environment.data.gov.uk/flood-monitoring/doc/reference",
    "version": "0.9",
    "comment": "Status: Beta service"
  },
  "items": {
    "@id": "http://environment.data.gov.uk/flood-monitoring/id/measures/2200TH-flow--Mean-15_min-m3_s",
    "label": "RIVER THAMES AT READING - flow--Mean-15_min-m3_s",
    "latestReading": {
      "@id": "http://environment.data.gov.uk/flood-monitoring/data/readings/2200TH-flow--Mean-15_min-m3_s/2026-02-20T13-15-00Z",
      "date": "2026-02-20",
      "dateTime": "2026-02-20T13:15:00Z",
      "measure": "http://environment.data.gov.uk/flood-monitoring/id/measures/2200TH-flow--Mean-15_min-m3_s",
      "value": 174.506
    },
    "notation": "2200TH-flow--Mean-15_min-m3_s",
    "parameter": "flow",
    "parameterName": "Flow",
    "period": 900,
    "station": "http://environment.data.gov.uk/flood-monitoring/id/stations/2200TH",
    "stationReference": "2200TH",
    "unit": "http://qudt.org/1.1/vocab/unit#CubicMeterPerSecond",
    "unitName": "m3/s",
    "valueType": "mean"
  }
}
```

**Critical Implementation Points:**
- The `items` field is an **object** (not an array) containing measurement metadata
- The actual latest reading is nested in `items.latestReading`
- Flow value is at `items.latestReading.value` (float, in m³/s)
- Timestamp is at `items.latestReading.dateTime` (ISO 8601 format with 'Z' timezone)
- **Note**: Older API versions may have returned `items` as an array. Implement detection for both structures for future-proofing.

### Weather Data HTML Parsing

The University of Reading weather page is HTML-formatted. 

**Observation Timestamp:**
The observation date and time are located in the first `<h2>` tag in the page body:

```html
<h2>
University of Reading METFiDAS weather observations for
20 Feb 2026  at time 1430 UTC
</h2>
```

**Temperature and Wind Data:**
The measurement data appears in a table structure:

```html
<table>
  <tr>
    <td>Air temperature: ºC</td>
    <td>9.7</td>
  </tr>
  <tr>
    <td>10-metre maximum 3-sec wind gust: m/s</td>
    <td>8.5</td>
  </tr>
</table>
```

However, when extracted as plain text, the format is:
```
Air temperature: ºC
9.7

10-metre maximum 3-sec wind gust: m/s
8.5
```

**Parsing Requirements:**

1. **Observation Timestamp**: 
   - Extract from first `<h2>` tag using: `soup.find('h2').get_text(strip=True)`
   - Format: "University of Reading METFiDAS weather observations for DD MMM YYYY at time HHMM UTC"
   - Display this full text to users (it's already human-readable)

2. **Temperature and Wind**:
   - The label and unit come **before** the numeric value (on separate lines when whitespace-collapsed)
   - Use regex patterns that account for whitespace:
     - Temperature: `Air temperature:\s*ºC\s*([-+]?\d+\.?\d*)`
     - Wind gust: `10-metre maximum 3-sec wind gust:\s*m/s\s*([-+]?\d+\.?\d*)`
   - Parse the full page text rather than trying to navigate HTML structure (which may change)

### Caching Implementation

**Critical Requirements:**

1. **Single Worker Requirement**: 
   - If using a multi-worker WSGI server (e.g., gunicorn with `--workers 2`), each worker process has its own separate memory space
   - In-memory cache dictionaries are **NOT shared** between workers
   - This causes inconsistent cache behavior, duplicate API calls, and unpredictable expiry
   
   **Solutions:**
   - Use a single worker: `gunicorn --workers 1`
   - OR implement shared cache using Redis/Memcached for multi-worker setups

2. **Cache Structure**:
   ```python
   cache = {
       'river_data': {...},          # Actual data from API
       'river_timestamp': datetime,   # When data was cached
       'weather_data': {...},         # Actual weather data
       'weather_timestamp': datetime  # When data was cached
   }
   ```

3. **Cache Expiry Logic**: 
   - Store both data AND timestamp when caching
   - On each request, check: `(current_time - cached_timestamp) > 15 minutes`
   - Use `timedelta(minutes=15)` for precise comparison
   - Clear timestamp to force refresh: `cache['river_timestamp'] = None`

4. **Force Refresh Mechanism**:
   - Implement a query parameter (e.g., `?force=true`) to bypass cache
   - When force refresh is requested:
     ```python
     cache['river_timestamp'] = None
     cache['weather_timestamp'] = None
     # Then proceed with normal cache check (will trigger refresh)
     ```
   - Connect this to the "Refresh Now" button in the UI

### Error Handling

1. **Network Failures**: 
   - Both external sources may be temporarily unavailable
   - Set appropriate timeouts (recommended: 10 seconds)
   - Handle HTTP errors gracefully:
     ```python
     try:
         response = requests.get(url, timeout=10)
         response.raise_for_status()
     except requests.RequestException as e:
         logger.error(f"Failed to fetch data: {e}")
         return None
     ```
   - Return HTTP 503 (Service Unavailable) to client if fresh data cannot be obtained
   - Consider displaying user-friendly error messages
   - Option: Keep using stale cached data if fresh data is unavailable

2. **Parsing Failures**: 
   - HTML/JSON structure may change over time
   - Log detailed errors including actual content received
   - Implement fallback to previous data structure if possible
   - Validate extracted values before using them

### Data Validation

Implement sanity checks on extracted values:

1. **River Flow**: 
   - Should be a positive number
   - Typical range: 10-300 m³/s for River Thames at Reading
   - Alert/log if outside this range

2. **Temperature**: 
   - Should be realistic: -20°C to 45°C absolute bounds
   - Typical range: -10°C to 35°C for UK

3. **Wind Speed**: 
   - Should be positive
   - Typical range: 0-30 m/s
   - Values above 35 m/s are unusual and should be logged

If values are outside expected ranges, log warnings and consider rejecting the data.

### Logging Requirements

Implement comprehensive logging for operations and debugging:

**Required Log Messages:**

```
INFO: River cache is empty
INFO: River cache age: 5.2 minutes
INFO: River cache is still valid
INFO: River cache expired - fetching fresh data
INFO: Fetching river data from [URL]
INFO: Successfully fetched river data: flow=174.5 m³/s at 2026-02-20T13:15:00Z
INFO: River cache updated successfully
ERROR: Failed to update river cache: [error details]

INFO: Weather cache age: 5.2 minutes
INFO: Weather cache is still valid
INFO: Parsed temperature: 9.7°C
INFO: Parsed wind gust: 8.5 m/s
INFO: Successfully fetched weather data: temp=9.7°C, wind=8.5 m/s

INFO: Force refresh requested - clearing cache
```

This logging is crucial for:
- Debugging cache behavior
- Monitoring external API reliability
- Verifying data refresh cycles
- Troubleshooting parsing issues

### Performance Considerations

1. **HTTP Timeouts**: Set appropriate timeouts to prevent hanging:
   ```python
   requests.get(url, timeout=10)  # 10 seconds
   ```

2. **Concurrent Requests**: 
   - Cache ensures multiple simultaneous page views don't trigger multiple API calls
   - Only the first request (when cache is empty/expired) hits the external APIs
   - Subsequent requests within 15 minutes use cached data

3. **Browser Auto-Refresh**: 
   - Frontend should poll server every 5 minutes
   - Server will return cached data if still valid (no external API calls)
   - Efficient: Most requests are served from cache

4. **External API Update Frequency**:
   - Environment Agency: Updates every 15 minutes
   - Weather station: Updates continuously
   - 15-minute cache aligns with EA update schedule

### Docker Deployment Considerations

When containerizing the application:

1. **Single Worker**: Use `gunicorn --workers 1` for cache consistency
2. **Logging**: Configure to stdout for `docker logs` visibility
3. **Timeouts**: Increase gunicorn timeout for slow API responses: `--timeout 120`
4. **Health Checks**: Consider implementing `/health` endpoint
5. **Proxy Settings**: May need HTTP_PROXY environment variables in corporate environments

Example Dockerfile CMD:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "--log-level", "info", "app:app"]
```

### Testing Recommendations

1. **Demo/Mock Mode**: 
   - Implement a DEMO_MODE environment variable
   - Returns static test data when enabled
   - Allows testing without external API dependencies
   - Useful for development and demonstrations

2. **Cache Testing**: 
   - Temporarily reduce `CACHE_EXPIRY_MINUTES = 0.5` (30 seconds)
   - Quickly verify cache expiry without waiting 15 minutes
   - **Remember to restore to 15 minutes for production!**

3. **Force Refresh Testing**: 
   - Always test the manual refresh button
   - Verify cache age resets to 0
   - Check logs show "Force refresh requested"

4. **Multi-Request Testing**: 
   - Make rapid successive requests
   - Verify only first request fetches data
   - Subsequent requests use cache

5. **Network Failure Simulation**:
   - Test with incorrect URLs
   - Test with network disconnected
   - Verify graceful error handling

### API Reliability & Monitoring

**Expected Behavior:**
- Environment Agency API: Very reliable, updated every 15 minutes
- University of Reading: Generally reliable, may have brief maintenance
- Both require internet connectivity (no authentication)

**Recommended Resilience Features:**

1. **Retry Logic**: 
   - Retry failed requests once after 2-second delay
   - Don't retry more than once to avoid delays

2. **Stale Data Tolerance**: 
   - Consider keeping last good data if APIs temporarily unavailable
   - Display warning to users: "Using data from [timestamp] - unable to refresh"

3. **Health Monitoring**:
   - Log all API failures
   - Track success/failure rates
   - Consider alerting if APIs unreachable for extended period

### Security Considerations

1. **Input Validation**: Always validate data from external sources before using
2. **HTML Parsing**: Use safe parsing libraries (BeautifulSoup) to prevent injection
3. **No Authentication Required**: Both APIs are public, no credentials to manage
4. **HTTPS**: Weather site uses HTTPS, ensuring data integrity

### Future Enhancements

Consider implementing:
- Historical data tracking (store readings in database)
- Trend analysis (rising/falling river levels)
- Email/SMS alerts when conditions change
- Mobile-responsive PWA
- Webhook notifications to club messaging systems

---

## Implementation Checklist

- [ ] Fetch from Environment Agency API with proper JSON parsing (`items.latestReading.value`)
- [ ] Parse University of Reading HTML with correct regex patterns
- [ ] Extract observation timestamp from first `<h2>` tag
- [ ] Implement 15-minute cache with timestamp checking
- [ ] Use single worker or shared cache solution
- [ ] Add force refresh mechanism (`?force=true`)
- [ ] Implement comprehensive logging
- [ ] Add data validation for extracted values
- [ ] Set HTTP timeouts (10 seconds)
- [ ] Handle network errors gracefully
- [ ] Display cache age in UI
- [ ] Add "Refresh Now" button
- [ ] Add clickable data source links (Environment Agency and University of Reading)
- [ ] Ensure links open in new tab with proper security attributes
- [ ] Implement frontend auto-refresh (5 minutes)
- [ ] Test cache expiry (can use 30-second expiry for quick test)
- [ ] Test force refresh functionality
- [ ] Verify logging shows cache decisions
- [ ] Test with real APIs and verify data accuracy
- [ ] Verify observation timestamp displays correctly
- [ ] Verify data source links work and open in new tabs
- [ ] Implement Demo Mode for testing without APIs
- [ ] Document deployment steps
- [ ] Create Docker container with single worker
- [ ] Test in production environment

---

## Reference

- Original spec: `spec.md`
- Safety rules: `rules.md`
- Implementation guide: See project README.md
- Troubleshooting: See NETWORK_TROUBLESHOOTING.md and CACHE_FIX_DOCUMENTATION.md
