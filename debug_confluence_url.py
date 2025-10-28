"""Debug Confluence URL construction."""
from urllib.parse import urljoin
import requests

# Test URL construction
base_url = "https://mmammidi.atlassian.net/wiki"
endpoint = "/rest/api/space"

# Test urljoin
constructed_url = urljoin(base_url, endpoint)
print(f"Base URL: {base_url}")
print(f"Endpoint: {endpoint}")
print(f"Constructed URL: {constructed_url}")

# Correct URL should be
correct_url = f"{base_url}{endpoint}"
print(f"Manual construction: {correct_url}")

# Test actual request
print("\nTesting actual request...")
try:
    # Try with credentials from env
    from config.settings import settings
    
    auth = (settings.CONFLUENCE_USERNAME, settings.CONFLUENCE_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    print(f"Requesting: {correct_url}")
    response = requests.get(correct_url, auth=auth, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Found {len(data.get('results', []))} spaces")
        if data.get('results'):
            print("\nAvailable spaces:")
            for space in data['results'][:5]:
                print(f"  - {space.get('key')}: {space.get('name')}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")

