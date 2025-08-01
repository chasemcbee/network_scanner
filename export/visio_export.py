import sqlite3
import win32com.client
from database_manager import get_active_database_path

def export_to_visio(db_path=None, filename="network_topology.vsdx"):
    if db_path is None:
        db_path = get_active_database_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT ip, hostname FROM fortinet_devices")
    firewalls = cursor.fetchall()

    cursor.execute("SELECT fg_ip, name, ip FROM fortinet_switches")
    switches = cursor.fetchall()

    cursor.execute("SELECT fg_ip, name, ip FROM fortinet_aps")
    aps = cursor.fetchall()

    cursor.execute("SELECT fg_ip, asset_name, ip, type FROM fortigate_assets")
    assets = cursor.fetchall()

    conn.close()

    visio = win32com.client.Dispatch("Visio.Application")
    visio.Visible = False
    doc = visio.Documents.Add("")
    page = visio.ActivePage

    x, y = 1, 9
    node_refs = {}

    def drop_shape(name, stencil="Rectangle", x=1, y=1):
        master = visio.Documents("Basic_U.VSS").Masters(stencil)
        shape = page.Drop(master, x, y)
        shape.Text = name
        return shape

    for ip, hostname in firewalls:
        label = hostname or ip
        shape = drop_shape(label, "Rounded Rectangle", x, y)
        node_refs[ip] = shape
        y -= 2

    for fg_ip, name, ip in switches:
        if fg_ip in node_refs:
            x2, y2 = x + 2, y + 1
            label = name or ip
            s = drop_shape(label, "Rectangle", x2, y2)
            page.DrawLine(node_refs[fg_ip].CellsU("PinX").ResultIU, node_refs[fg_ip].CellsU("PinY").ResultIU,
                          s.CellsU("PinX").ResultIU, s.CellsU("PinY").ResultIU)

    for fg_ip, name, ip in aps:
        if fg_ip in node_refs:
            x2, y2 = x + 3, y
            label = name or ip
            s = drop_shape(label, "Rectangle", x2, y2)
            page.DrawLine(node_refs[fg_ip].CellsU("PinX").ResultIU, node_refs[fg_ip].CellsU("PinY").ResultIU,
                          s.CellsU("PinX").ResultIU, s.CellsU("PinY").ResultIU)

    for fg_ip, name, ip, _ in assets:
        if fg_ip in node_refs:
            x2, y2 = x + 4, y - 1
            label = name or ip
            s = drop_shape(label, "Rectangle", x2, y2)
            page.DrawLine(node_refs[fg_ip].CellsU("PinX").ResultIU, node_refs[fg_ip].CellsU("PinY").ResultIU,
                          s.CellsU("PinX").ResultIU, s.CellsU("PinY").ResultIU)

    full_path = filename if filename.endswith(".vsdx") else filename + ".vsdx"
    doc.SaveAs(full_path)
    visio.Quit()

    print(f"[+] Visio topology exported to {full_path}")
