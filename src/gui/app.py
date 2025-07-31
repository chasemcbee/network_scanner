import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import sys

# Ensure scanner modules are accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scanner.cisco_scanner import scan_cisco_devices
from scanner.fortinet_scanner import scan_fortinet_devices
from scanner.fortimanager_scanner import scan_fortimanager_devices
from scanner.discovery_engine import build_inventory
from scanner.visio_export import export_to_visio

class NetworkScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Scanner")
        self.build_gui()

    def build_gui(self):
        self.tabControl = ttk.Notebook(self.root)
        self.scan_tab = ttk.Frame(self.tabControl)
        self.output_tab = ttk.Frame(self.tabControl)

        self.tabControl.add(self.scan_tab, text='Scan')
        self.tabControl.add(self.output_tab, text='Output')
        self.tabControl.pack(expand=1, fill="both")

        # Input Fields
        ttk.Label(self.scan_tab, text="IP Range/Subnet:").grid(row=0, column=0, sticky='e')
        self.ip_entry = ttk.Entry(self.scan_tab, width=40)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.scan_tab, text="Username:").grid(row=1, column=0, sticky='e')
        self.username_entry = ttk.Entry(self.scan_tab)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.scan_tab, text="Password:").grid(row=2, column=0, sticky='e')
        self.password_entry = ttk.Entry(self.scan_tab, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.scan_tab, text="FortiGate API Token:").grid(row=3, column=0, sticky='e')
        self.api_entry = ttk.Entry(self.scan_tab)
        self.api_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.scan_tab, text="FortiManager IP:").grid(row=4, column=0, sticky='e')
        self.fmg_ip_entry = ttk.Entry(self.scan_tab)
        self.fmg_ip_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(self.scan_tab, text="FortiManager Token:").grid(row=5, column=0, sticky='e')
        self.fmg_token_entry = ttk.Entry(self.scan_tab)
        self.fmg_token_entry.grid(row=5, column=1, padx=5, pady=5)

        # Buttons
        self.scan_button = ttk.Button(self.scan_tab, text="Start Scan", command=self.start_scan)
        self.scan_button.grid(row=6, column=1, pady=10)

        self.export_excel_button = ttk.Button(self.scan_tab, text="Open Excel", command=self.open_excel)
        self.export_excel_button.grid(row=7, column=0, pady=10)

        self.export_visio_button = ttk.Button(self.scan_tab, text="Open Visio", command=self.open_visio)
        self.export_visio_button.grid(row=7, column=1, pady=10)

        # Output log window
        self.output_text = tk.Text(self.output_tab, wrap='word')
        self.output_text.pack(expand=1, fill='both')

    def start_scan(self):
        self.output_text.insert(tk.END, "Starting scan...\n")
        threading.Thread(target=self.scan_network).start()

    def scan_network(self):
        ip_range = self.ip_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        api_token = self.api_entry.get()
        fmg_ip = self.fmg_ip_entry.get()
        fmg_token = self.fmg_token_entry.get()

        devices = []

        self.output_text.insert(tk.END, "Scanning Cisco devices...\n")
        try:
            devices += scan_cisco_devices(ip_range, username, password)
        except Exception as e:
            self.output_text.insert(tk.END, f"Cisco scan error: {e}\n")

        self.output_text.insert(tk.END, "Scanning Fortinet devices (FortiGate)...\n")
        try:
            devices += scan_fortinet_devices(ip_range, api_token)
        except Exception as e:
            self.output_text.insert(tk.END, f"Fortinet scan error: {e}\n")

        self.output_text.insert(tk.END, "Scanning FortiManager inventory...\n")
        try:
            devices += scan_fortimanager_devices(fmg_ip, fmg_token)
        except Exception as e:
            self.output_text.insert(tk.END, f"FortiManager scan error: {e}\n")

        self.output_text.insert(tk.END, "Building Excel inventory...\n")
        build_inventory(devices)

        self.output_text.insert(tk.END, "Generating Visio diagram...\n")
        export_to_visio(devices)

        self.output_text.insert(tk.END, "Scan complete. Output saved to Desktop.\n")
        messagebox.showinfo("Scan Complete", "Inventory and diagram exported to Desktop.")

    def open_excel(self):
        path = os.path.join(os.path.expanduser("~"), "Desktop", "network_inventory.xlsx")
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showwarning("Excel not found", "No Excel file was found on your Desktop.")

    def open_visio(self):
        path = os.path.join(os.path.expanduser("~"), "Desktop", "network_topology.vsdx")
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showwarning("Visio not found", "No Visio file was found on your Desktop.")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScannerApp(root)
    root.mainloop()
