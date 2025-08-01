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

def parse_wlac_vap(output, fg_ip):
    aps = []
    entries = output.split("\n\n")
    for block in entries:
        lines = block.strip().splitlines()
        ap = {"fg_ip": fg_ip, "source": "fortigate (ssh)"}
        for line in lines:
            if "vap-name" in line:
                ap["vap_name"] = line.split(":")[1].strip()
            elif "ssid" in line:
                ap["ssid"] = line.split(":")[1].strip()
            elif "bssid" in line:
                ap["bssid"] = line.split(":")[1].strip()
            elif "radio-id" in line:
                ap["radio_id"] = line.split(":")[1].strip()
            elif "band" in line:
                ap["band"] = line.split(":")[1].strip()
            elif "vlan-id" in line:
                ap["vlan_id"] = line.split(":")[1].strip()
            elif "intf" in line:
                ap["interface"] = line.split(":")[1].strip()
            elif "wtp-name" in line:
                ap["ap_name"] = line.split(":")[1].strip()
            elif "wtp-ip" in line:
                ap["ap_ip"] = line.split(":")[1].strip()
        if "ap_name" in ap and "ap_ip" in ap:
            aps.append(ap)
    return aps

def parse_switch_system_info(output, fg_ip):
    switches = []
    blocks = output.split("\n\n")
    for block in blocks:
        lines = block.strip().splitlines()
        sw = {"fg_ip": fg_ip, "source": "fortigate (ssh)"}
        for line in lines:
            if "hostname" in line:
                sw["hostname"] = line.split(":")[1].strip()
            elif "ip" in line and "ip6" not in line:
                sw["ip"] = line.split(":")[1].strip()
            elif "model" in line:
                sw["model"] = line.split(":")[1].strip()
            elif "serial" in line:
                sw["serial"] = line.split(":")[1].strip()
            elif "version" in line:
                sw["version"] = line.split(":")[1].strip()
            elif "status" in line:
                sw["status"] = line.split(":")[1].strip()
        if "ip" in sw:
            switches.append(sw)
    return switches

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

        sw_data = call_api(ip, api_key, "cmdb/switch-controller/managed-switch")
        if sw_data and sw_data.get("results"):
            for s in sw_data["results"]:
                save_to_db("fortinet_switches",
                    ["fg_ip TEXT", "name TEXT", "ip TEXT", "model TEXT", "source TEXT"],
                    [ip, s.get("name", ""), s.get("ip", ""), s.get("model", ""), "fortigate"])
        else:
            print("[!] FortiGate switch error or no results")

        ap_data = call_api(ip, api_key, "cmdb/wireless-controller/wtp")
        if ap_data and ap_data.get("results"):
            for a in ap_data["results"]:
                save_to_db("fortinet_aps",
                    ["fg_ip TEXT", "name TEXT", "ip TEXT", "model TEXT", "source TEXT"],
                    [ip, a.get("name", ""), a.get("ip", ""), a.get("model", ""), "fortigate"])
        else:
            print("[!] FortiGate AP error or no results")

    if ssh_username and ssh_password:
        sw_ssh_output = ssh_command(ip, ssh_username, ssh_password, "diagnose switch-controller switch-info")

        system_output = ssh_command(ip, ssh_username, ssh_password, "diagnose switch-controller system-info show")
        if system_output:
            switch_list = parse_switch_system_info(system_output, ip)
            for sw in switch_list:
                save_to_db("fortinet_switches",
                    ["fg_ip TEXT", "hostname TEXT", "ip TEXT", "model TEXT", "serial TEXT", "version TEXT", "status TEXT", "source TEXT"],
                    [sw.get("fg_ip", ""), sw.get("hostname", ""), sw.get("ip", ""), sw.get("model", ""), sw.get("serial", ""), sw.get("version", ""), sw.get("status", ""), sw.get("source", "")])

        ap_ssh_output = ssh_command(ip, ssh_username, ssh_password, "diagnose wireless-controller wlac -c wtp")

        vap_output = ssh_command(ip, ssh_username, ssh_password, "get wireless-controller wlac vap")
        if vap_output:
            aps = parse_wlac_vap(vap_output, ip)
            for ap in aps:
                save_to_db("fortinet_aps",
                    ["fg_ip TEXT", "ap_name TEXT", "ap_ip TEXT", "vap_name TEXT", "ssid TEXT", "bssid TEXT", "radio_id TEXT", "band TEXT", "vlan_id TEXT", "interface TEXT", "source TEXT"],
                    [ap.get("fg_ip", ""), ap.get("ap_name", ""), ap.get("ap_ip", ""), ap.get("vap_name", ""), ap.get("ssid", ""), ap.get("bssid", ""), ap.get("radio_id", ""), ap.get("band", ""), ap.get("vlan_id", ""), ap.get("interface", ""), ap.get("source", "")])

        asset_output = ssh_command(ip, ssh_username, ssh_password, "diagnose user device list")
        if asset_output:
            assets = parse_device_list(asset_output)
            for name, asset_ip, typ, src in assets:
                save_to_db("fortinet_endpoints",
                    ["fg_ip TEXT", "name TEXT", "ip TEXT", "type TEXT", "source TEXT"],
                    [ip, name, asset_ip, typ, src])
