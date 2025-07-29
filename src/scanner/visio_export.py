import os

def export_to_visio(devices):
    try:
        # This is a placeholder. Replace with actual Visio export logic.
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path = os.path.join(desktop, "network_topology.vsdx")
        with open(file_path, "w") as f:
            f.write("This is a placeholder Visio file.\n")
            for d in devices:
                f.write(f"{d['ip']} - {d['model']} ({d['vendor']})\n")
    except Exception as e:
        print(f"Visio export failed: {e}")
