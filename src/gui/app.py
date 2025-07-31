import tkinter as tk
from tkinter import ttk, messagebox
import threading

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scanner.cisco_scanner import scan_cisco_devices
from scanner.fortinet_scanner import scan_fortinet_devices
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

        # Scan tab inputs
        ttk.Label(self.scan_tab, text="IP Range/Subnet:").grid(row=0, column=0, sticky='e')
        self.ip_entry = ttk.Entry(self.scan_tab, width=40)
        self.ip_entry.grid(row=0, column=1)

        ttk.Label(self.scan_tab, text="Username:").grid(row=1, column=0, sticky='e')
        self.username_entry = ttk.Entry(self.scan_tab)
        self.username_entry.grid(row=1, column=1)

        ttk.Label(self.scan_tab, text="Password:").grid(row=2, column=0, sticky='e')
        self.password_entry = ttk.Entry(self.scan_tab, show="*")
        self.password_entry.grid(row=2, column=1)

        ttk.Label(self.scan_tab, text="Fortinet API Token:").grid(row=3, column=0, sticky='e')
        self.api_entry = ttk.Entry(self.scan_tab)
        self.api_entry.grid(row=3, column=1)

        self.scan_button = ttk.Button(self.scan_tab, text="Start Scan", command=self.start_scan)
        self.scan_button.grid(row=4, column=1, pady=10)

        self.output_text = tk.Text(self.output_tab, wrap='word')
        self.output_text.pack(expand=1, fill='both')

    def start_scan(self):
        self.output_text.insert(tk.END, "Starting scan...\n")
        t = threading.Thread(target=self.scan_network)
        t.start()

    def scan_network(self):
        ip_range = self.ip_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        api_token = self.api_entry.get()

        devices = []

        self.output_text.insert(tk.END, "Scanning Cisco devices...\n")
        devices += scan_cisco_devices(ip_range, username, password)

        self.output_text.insert(tk.END, "Scanning Fortinet devices...\n")
        devices += scan_fortinet_devices(ip_range, api_token)

        self.output_text.insert(tk.END, "Building Excel inventory...\n")
        build_inventory(devices)

        self.output_text.insert(tk.END, "Generating Visio diagram...\n")
        export_to_visio(devices)

        self.output_text.insert(tk.END, "Scan complete. Output saved to Desktop.\n")
        messagebox.showinfo("Scan Complete", "Inventory and diagram exported to Desktop.")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScannerApp(root)
    root.mainloop()