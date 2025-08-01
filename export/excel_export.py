import sqlite3
import pandas as pd
from database_manager import get_active_database_path

def export_to_excel(db_path=None, identities=None, filename="fortinet_inventory.xlsx"):
    if db_path is None:
        db_path = get_active_database_path()

    conn = sqlite3.connect(db_path)

    devices_df = pd.read_sql_query("SELECT * FROM fortinet_devices", conn)
    switches_df = pd.read_sql_query("SELECT * FROM fortinet_switches", conn)
    aps_df = pd.read_sql_query("SELECT * FROM fortinet_aps", conn)
    assets_df = pd.read_sql_query("SELECT * FROM fortigate_assets", conn)
    assets_df = assets_df.sort_values(by="asset_name", na_position="last")

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        devices_df.to_excel(writer, sheet_name="Devices", index=False)
        switches_df.to_excel(writer, sheet_name="Switches", index=False)
        aps_df.to_excel(writer, sheet_name="Access Points", index=False)
        assets_df.to_excel(writer, sheet_name="Assets", index=False)

        workbook = writer.book
        for sheet in writer.sheets.values():
            for col in sheet.iter_cols(min_row=1, max_row=1):
                for cell in col:
                    cell.font = cell.font.copy(bold=True)

    conn.close()
    print(f"[+] Exported to {filename}")
