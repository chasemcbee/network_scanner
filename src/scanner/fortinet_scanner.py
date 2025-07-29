import requests

def scan_fortinet_devices(ip_range, api_token):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    ips = ip_range.split(',')
    devices = []

    for ip in ips:
        try:
            url = f"https://{ip.strip()}/api/v2/monitor/system/status"
            resp = requests.get(url, headers=headers, verify=False, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                devices.append({
                    'ip': ip.strip(),
                    'vendor': 'Fortinet',
                    'model': data.get('model', 'Unknown'),
                    'serial': data.get('serial', 'Unknown'),
                    'version': data.get('version', 'Unknown')
                })
        except Exception as e:
            continue  # Skip failed IPs

    return devices
