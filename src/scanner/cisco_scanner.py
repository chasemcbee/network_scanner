import paramiko
import re

def run_commands(ip, username, password):
    commands = [
        'show version',
        'show inventory',
        'show cdp neighbors detail',
        'show lldp neighbors detail'
    ]
    output = {}
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=username, password=password, timeout=5)

        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd)
            output[cmd] = stdout.read().decode()

        client.close()
        return output
    except Exception as e:
        return {"error": str(e)}

def parse_cisco_output(output):
    version = re.search(r'Cisco IOS Software, .+ Version ([\S]+),', output.get('show version', ''), re.M)
    serial = re.search(r'System serial number\s*:\s*(\S+)', output.get('show inventory', ''), re.M)
    model = re.search(r'PID:\s*(\S+)', output.get('show inventory', ''), re.M)

    return {
        'ip': output.get('ip', 'unknown'),
        'vendor': 'Cisco',
        'model': model.group(1) if model else 'Unknown',
        'serial': serial.group(1) if serial else 'Unknown',
        'version': version.group(1) if version else 'Unknown'
    }

def scan_cisco_devices(ip_range, username, password):
    ips = ip_range.split(',')  # For simplicity
    devices = []
    for ip in ips:
        raw = run_commands(ip.strip(), username, password)
        if "error" not in raw:
            raw['ip'] = ip
            devices.append(parse_cisco_output(raw))
    return devices
