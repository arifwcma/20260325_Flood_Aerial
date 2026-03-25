import arcpy
import os
import sys
import time

APRX_PATH = r"I:\Jobs\20252026\Savio\20260325_Flood_Aerial\flood_aerial.aprx"

EXPECTED = [
    ("AIG Aerial Photos", "AIG Aerial Overlays"),
    ("AIG Aerial Photos", "AIG Photo Locations"),
    ("Linescans", "RGB Linescans"),
    ("Linescans", "Non-RGB Linescans"),
    ("Satellite Imagery", "kerang-vh_2022nov16_sat_sar_3m_epsg28354"),
    ("Satellite Imagery", "kerang-vv_2022nov16_sat_sar_3m_epsg28354"),
    ("Satellite Imagery", "kerang_2022nov18_sat_vis_150cm_epsg32754"),
    ("Satellite Imagery", "echuca-shepparton-vh_2022nov18_sat_sar_3m_epsg28354"),
    ("Satellite Imagery", "echuca-shepparton-vv_2022nov18_sat_sar_3m_epsg28354"),
    ("FireMapper", "FireMapper Photo Locations"),
    ("CMA Features", None),
    ("SnapSendSolve", "SnapSendSolve Reports"),
    ("Wimmera", None),
]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()


def main():
    log("=" * 60)
    log("  PROJECT CHECK")
    log("=" * 60)

    if not os.path.exists(APRX_PATH):
        log(f"ERROR: Project not found: {APRX_PATH}")
        return

    aprx = arcpy.mp.ArcGISProject(APRX_PATH)
    maps = aprx.listMaps()
    if not maps:
        log("ERROR: No maps in project")
        return

    m = maps[0]
    log(f"Map: {m.name}")
    log(f"CRS: {m.spatialReference.name}")
    log("")

    all_layers = m.listLayers()
    all_tables = m.listTables()

    log(f"Total layers: {len(all_layers)}")
    log(f"Total tables: {len(all_tables)}")
    log("")

    log("--- LAYERS ---")
    group_contents = {}
    for lyr in all_layers:
        if lyr.isGroupLayer:
            log(f"  [GROUP] {lyr.name}")
            group_contents[lyr.name] = []
        elif lyr.isBasemapLayer:
            log(f"  [BASEMAP] {lyr.name}")
        else:
            parent = lyr.longName.split("\\")[0] if "\\" in lyr.longName else "(root)"
            log(f"  {lyr.name}  ({parent})")
            if parent != "(root)":
                group_contents.setdefault(parent, []).append(lyr.name)
            else:
                group_contents.setdefault("(root)", []).append(lyr.name)

    if all_tables:
        log("")
        log("--- TABLES ---")
        for tbl in all_tables:
            log(f"  {tbl.name}")

    layer_names = {lyr.name for lyr in all_layers if not lyr.isGroupLayer and not lyr.isBasemapLayer}
    group_names = {lyr.name for lyr in all_layers if lyr.isGroupLayer}
    table_names = {tbl.name for tbl in all_tables}
    all_names = layer_names | table_names

    log("")
    log("--- EXPECTED vs FOUND ---")
    found = []
    missing = []

    for group, name in EXPECTED:
        if name is None:
            if group in group_names:
                members = group_contents.get(group, [])
                if members:
                    log(f"  OK   {group} ({len(members)} layers)")
                    found.append(f"{group} ({len(members)} layers)")
                else:
                    log(f"  MISS {group} (group exists but empty)")
                    missing.append(f"{group} (empty group)")
            else:
                has_any = any(group.lower() in n.lower() for n in all_names)
                if has_any:
                    log(f"  OK   {group} (found without group)")
                    found.append(group)
                else:
                    log(f"  MISS {group}")
                    missing.append(group)
        else:
            if name in all_names:
                log(f"  OK   {name}")
                found.append(name)
            else:
                partial = [n for n in all_names if name.lower() in n.lower()]
                if partial:
                    log(f"  OK~  {name} (partial match: {partial[0]})")
                    found.append(name)
                else:
                    log(f"  MISS {name}")
                    missing.append(f"{group} / {name}")

    log("")
    log("=" * 60)
    log(f"  RESULT: {len(found)} found, {len(missing)} missing")
    log("=" * 60)

    if missing:
        log("")
        log("MISSING:")
        for m_item in missing:
            log(f"  - {m_item}")
    else:
        log("")
        log("All expected resources are present.")


if __name__ == "__main__":
    main()
