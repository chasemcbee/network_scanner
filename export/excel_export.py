import sqlite3
import pandas as pd
from database_manager import get_active_database_path

def export_to_excel(db_path=None, hostname_filter=None, type_filter=None, filename="fortinet_inventory.xlsx"):
    if db_path is None:
        db_path = get_active_database_path()

    conn = sqlite3.connect(db_path)

    def safe_query(table):
        try:
            return pd.read_sql_query(f"SELECT * FROM {table}", conn)
        except:
            return pd.DataFrame()

    devices_df = safe_query("fortinet_devices")
    switches_df = safe_query("fortinet_switches")
    aps_df = safe_query("fortinet_aps")
    endpoints_df = safe_query("fortinet_endpoints")

    # Sort switches by hostname if available
    if not switches_df.empty:
        if "hostname" in switches_df.columns:
            switches_df = switches_df.sort_values(by="hostname", na_position="last")
        elif "name" in switches_df.columns:
            switches_df = switches_df.sort_values(by="name", na_position="last")

    # Sort APs by ap_name or name
    if not aps_df.empty:
        if "ap_name" in aps_df.columns:
            aps_df = aps_df.sort_values(by="ap_name", na_position="last")
        elif "name" in aps_df.columns:
            aps_df = aps_df.sort_values(by="name", na_position="last")

    # Filter endpoints
    if not endpoints_df.empty:
        if hostname_filter:
            endpoints_df = endpoints_df[endpoints_df["name"].str.contains(hostname_filter, case=False, na=False)]
        if type_filter:
            endpoints_df = endpoints_df[endpoints_df["type"].str.contains(type_filter, case=False, na=False)]

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        if not devices_df.empty:
            devices_df.to_excel(writer, sheet_name="Devices", index=False)
        if not switches_df.empty:
            switches_df.to_excel(writer, sheet_name="Switches", index=False)
        if not aps_df.empty:
            aps_df.to_excel(writer, sheet_name="Access Points", index=False)
        if not endpoints_df.empty:
            endpoints_df.to_excel(writer, sheet_name="Endpoints", index=False)

        workbook = writer.book
        for sheet in writer.sheets.values():
            for col in sheet.iter_cols(min_row=1, max_row=1):
                for cell in col:
                    cell.font = cell.font.copy(bold=True)

    conn.close()
    print(f"[+] Exported to {filename}")
