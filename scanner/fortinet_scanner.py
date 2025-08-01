import requests
import sqlite3
import paramiko
import re
import json
from database_manager import get_active_database_path

requests.packages.urllib3.disable_warnings()

def save_to_db(table, columns, values):
    db_path = get_active_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check existing columns if table already exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    if cursor.fetchone():
        cursor.execute(f"PRAGMA table_info({table})")
        existing_cols = [col[1] for col in cursor.fetchall()]
        if len(existing_cols) != len(columns):
            print(f"[!] Column mismatch in {table}, dropping and recreating")
            cursor.execute(f"DROP TABLE IF EXISTS {table}")

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            {', '.join(columns)}
        )
    """)
    cursor.execute(f"INSERT INTO {table} VALUES ({', '.join(['?' for _ in values])})", values)
    conn.commit()
    conn.close()

def ssh_command(ip, username, password, command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=username, password=password, timeout=10)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        client.close()
        return output
    except Exception as e:
        print(f"[!] SSH error on {ip}: {e}")
        return ""

def parse_device_list(output):
    entries = []
    hosts = output.split('\nvd root/0')
    for h in hosts:
        ip_match = re.search(r'ip (\d+\.\d+\.\d+\.\d+)', h)
        name_match = re.search(r"host '([^']+)'", h)
        type_match = re.search(r"type '([^']+)'", h)
        if ip_match:
            entries.append((name_match.group(1) if name_match else '', ip_match.group(1), type_match.group(1) if type_match else '', 'fortigate'))
    return entries

def call_api(ip, api_key, endpoint):
    url = f"https://{ip}/api/v2/{endpoint}"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=10)
        print(f"[DEBUG] FortiGate /{endpoint} response: {r.status_code}")
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        print(f"[!] API call error to {endpoint}: {e}")
        return None

def scan_fortigate(ip, api_key=None, ssh_username=None, ssh_password=None):
    print(f"--- FortiGate: {ip} ---")

    if api_key:
        sys_data = call_api(ip, api_key, "monitor/system/status")
        if sys_data:
            info = sys_data.get("result", {}) or sys_data.get("system_status", {})
            save_to_db("fortinet_devices",
                ["ip TEXT", "hostname TEXT", "serial TEXT", "version TEXT", "model TEXT", "source TEXT", "type TEXT", "mgmt_vdom TEXT"],
                [ip, info.get("hostname", ""), info.get("serial", ""), info.get("version", ""), info.get("model", ""), "fortigate", "firewall", info.get("mgmt_vdom", "root")])
        else:
            print("[!] FortiGate status failed")

        # Switches
        sw_data = call_api(ip, api_key, "cmdb/switch-controller/managed-switch")
        if sw_data and sw_data.get("results"):
            for s in sw_data["results"]:
                save_to_db("fortinet_switches",
                    ["fg_ip TEXT", "name TEXT", "ip TEXT", "model TEXT", "source TEXT"],
                    [ip, s.get("name", ""), s.get("ip", ""), s.get("model", ""), "fortigate"])
        else:
            print("[!] FortiGate switch error or no results")

        # APs
        ap_data = call_api(ip, api_key, "cmdb/wireless-controller/wtp")
        if ap_data and ap_data.get("results"):
            for a in ap_data["results"]:
                save_to_db("fortinet_aps",
                    ["fg_ip TEXT", "name TEXT", "ip TEXT", "model TEXT", "source TEXT"],
                    [ip, a.get("name", ""), a.get("ip", ""), a.get("model", ""), "fortigate"])
        else:
            print("[!] FortiGate AP error or no results")

    if ssh_username and ssh_password:
        raw = ssh_command(ip, ssh_username, ssh_password, "diagnose user device list")
        if raw:
            assets = parse_device_list(raw)
            if assets:
                for a in assets:
                    save_to_db("fortigate_assets",
                        ["fg_ip TEXT", "asset_name TEXT", "ip TEXT", "type TEXT", "source TEXT"],
                        (ip, a[0], a[1], a[2], "ssh"))
            else:
                print("[!] No parsed data for fortigate_assets")
        else:
            print("[!] No SSH response for asset discovery")
