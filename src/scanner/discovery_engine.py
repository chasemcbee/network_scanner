import openpyxl
import os

def build_inventory(devices):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Network Inventory"
    ws.append(["IP Address", "Vendor", "Model", "Serial Number", "Version"])

    for d in devices:
        ws.append([
            d.get("ip", ""),
            d.get("vendor", ""),
            d.get("model", ""),
            d.get("serial", ""),
            d.get("version", "")
        ])

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop, "network_inventory.xlsx")
    wb.save(file_path)
