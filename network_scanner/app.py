import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel, StringVar, OptionMenu
import os

from scanner.fortinet_scanner import scan_fortigate
from export.excel_export import export_to_excel
from export.visio_export import export_to_visio
from database_manager import list_databases, create_database, set_active_database, get_active_database_path

# === GUI SETUP ===
root = tk.Tk()
root.title("Network Scanner")

# === FORTIGATE INPUTS ===
tk.Label(root, text="FortiGate IP:").grid(row=0, column=0)
ip_entry = tk.Entry(root)
ip_entry.grid(row=0, column=1)

tk.Label(root, text="FortiGate API Key:").grid(row=1, column=0)
api_entry = tk.Entry(root)
api_entry.grid(row=1, column=1)

api_var = tk.BooleanVar(value=True)
api_toggle = tk.Checkbutton(root, text="Use FortiGate API", variable=api_var)
api_toggle.grid(row=1, column=2)

tk.Label(root, text="SSH Username:").grid(row=2, column=0)
ssh_user_entry = tk.Entry(root)
ssh_user_entry.grid(row=2, column=1)

tk.Label(root, text="SSH Password:").grid(row=3, column=0)
ssh_pass_entry = tk.Entry(root, show="*")
ssh_pass_entry.grid(row=3, column=1)

# === FILTER OPTIONS ===
tk.Label(root, text="Filter by Endpoint Hostname (optional):").grid(row=5, column=0)
hostname_filter_entry = tk.Entry(root)
hostname_filter_entry.grid(row=5, column=1)

tk.Label(root, text="Filter by Endpoint Type (optional):").grid(row=6, column=0)
type_filter_entry = tk.Entry(root)
type_filter_entry.grid(row=6, column=1)

# === ACTION BUTTONS ===
tk.Button(root, text="Run Scan", command=lambda: scan_fortigate(
    ip_entry.get(),
    api_key=api_entry.get().strip() if api_var.get() else None,
    ssh_username=ssh_user_entry.get(),
    ssh_password=ssh_pass_entry.get()
)).grid(row=4, column=0, pady=10)

tk.Button(root, text="Export to Excel", command=lambda: export_to_excel(
    get_active_database_path(),
    hostname_filter=hostname_filter_entry.get().strip(),
    type_filter=type_filter_entry.get().strip()
)).grid(row=4, column=1)

tk.Button(root, text="Export to Visio", command=lambda: export_to_visio(
    get_active_database_path(),
    hostname_filter=hostname_filter_entry.get().strip(),
    type_filter=type_filter_entry.get().strip()
)).grid(row=4, column=2)

# === DATABASE MENU ===
def show_database_menu():
    win = Toplevel(root)
    win.title("Select Database")

    tk.Label(win, text="Select an existing database:").pack()
    dbs = list_databases()
    selected = StringVar(win)
    if dbs:
        selected.set(dbs[0])
    dropdown = OptionMenu(win, selected, *dbs)
    dropdown.pack()

    def select():
        set_active_database(selected.get())
        messagebox.showinfo("Database", f"Switched to {selected.get()}")
        win.destroy()

    def create_new():
        new_name = simpledialog.askstring("New Database", "Enter new database name:")
        if new_name:
            if not new_name.endswith(".db"):
                new_name += ".db"
            path = create_database(new_name.replace(".db", ""))
            messagebox.showinfo("Database", f"Created new database: {os.path.basename(path)}")
            win.destroy()

    tk.Button(win, text="Use Selected", command=select).pack(pady=5)
    tk.Button(win, text="Create New Database", command=create_new).pack()

# Add menubar
menubar = tk.Menu(root)
db_menu = tk.Menu(menubar, tearoff=0)
db_menu.add_command(label="Select or Create...", command=show_database_menu)
menubar.add_cascade(label="Database", menu=db_menu)
root.config(menu=menubar)

root.mainloop()
