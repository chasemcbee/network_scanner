import requests

def scan_fortimanager_devices(ip, api_token):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    url = f"https://{ip}/jsonrpc"
    devices = []

    payload = {
        "method": "get",
        "params": [
            {
                "url": "/dvmdb/device"
            }
        ],
        "id": 1,
        "session": api_token
    }

    try:
        response = requests.post(url, json=payload, headers=headers, verify=False, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if "result" in data and data["result"]:
                for item in data["result"][0].get("data", []):
                    device_type = item.get("desc", "").lower()
                    model = item.get("platform_str", item.get("platform", "Unknown"))
                    serial = item.get("sn", "Unknown")
                    version = item.get("os_ver", "Unknown")
                    device_id = serial or item.get("name", "Unknown")
                    mgmt_ip = item.get("mgmt_ip", "Unknown")

                    if "switch" in device_type:
                        dtype = "Switch"
                    elif "ap" in device_type or "access point" in device_type:
                        dtype = "Access Point"
                    elif "firewall" in device_type or "fortigate" in device_type:
                        dtype = "Firewall"
                    else:
                        dtype = "Device"

                    devices.append({
                        "ip": mgmt_ip,
                        "vendor": "Fortinet",
                        "model": model,
                        "serial": serial,
                        "version": version,
                        "device_type": dtype,
                        "id": device_id,
                        "connected_to": None  # Not available from FMG directly
                    })
        else:
            print(f"FortiManager API returned status {response.status_code}")

    except Exception as e:
        print(f"FortiManager scan error: {e}")

    return devices
