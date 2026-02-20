import requests
import traceback

print("Testing River API...")
try:
    r = requests.get('http://environment.data.gov.uk/flood-monitoring/id/measures/2200TH-flow--Mean-15_min-m3_s', timeout=10)
    print(f'Status: {r.status_code}')
    print(f'Content length: {len(r.content)}')
    print(f'Response: {r.text[:200]}')
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()

print("\nTesting Weather URL...")
try:
    r = requests.get('https://www.met.reading.ac.uk/weatherdata/Reading_AWS_weather_report.html', timeout=10)
    print(f'Status: {r.status_code}')
    print(f'Content length: {len(r.content)}')
    print(f'Response: {r.text[:200]}')
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()
