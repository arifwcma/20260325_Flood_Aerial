import arcpy
import os
import sys
import time

APRX_PATH = r"I:\Jobs\20252026\Savio\20260325_Flood_Aerial\flood_aerial.aprx"
SHP_PATH = r"I:\Jobs\20252026\Savio\20260325_Flood_Aerial\data\boundary\boundary.shp"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()


def main():
    log("=== TEST 2: add a shapefile to aprx ===")

    if not os.path.exists(SHP_PATH):
        log(f"ERROR: Shapefile not found: {SHP_PATH}")
        return

    if not os.path.exists(APRX_PATH):
        log(f"ERROR: Project not found: {APRX_PATH}")
        return

    log(f"Opening project: {APRX_PATH}")
    aprx = arcpy.mp.ArcGISProject(APRX_PATH)

    maps = aprx.listMaps()
    log(f"  Maps found: {len(maps)}")
    for i, m in enumerate(maps):
        log(f"    [{i}] {m.name} ({len(m.listLayers())} layers)")

    if not maps:
        log("ERROR: No maps in project")
        return

    m = maps[0]
    log(f"Using map: {m.name}")

    log(f"Adding shapefile: {SHP_PATH}")
    lyr = m.addDataFromPath(SHP_PATH)
    log(f"  addDataFromPath returned: {lyr}")

    if lyr:
        log(f"  Layer name: {lyr.name}")
        log(f"  Layer type: {lyr.dataSource if hasattr(lyr, 'dataSource') else 'unknown'}")

    log("Saving project...")
    aprx.save()
    log("Done. Open the .aprx in ArcGIS Pro to verify.")


if __name__ == "__main__":
    main()
