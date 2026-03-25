import arcpy
import os
import sys
import time

APRX_PATH = r"I:\Jobs\20252026\Savio\20260325_Flood_Aerial\flood_aerial.aprx"
KML_PATH = r"I:\Raster\October 2022 Flood Imagery_20230517\AIG\1007\2022_10_07_035503_00_00_V_001.kml"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()


def main():
    log("=== TEST 3: add KML directly via addDataFromPath ===")

    if not os.path.exists(KML_PATH):
        log(f"ERROR: KML not found: {KML_PATH}")
        return

    log(f"Opening project: {APRX_PATH}")
    aprx = arcpy.mp.ArcGISProject(APRX_PATH)
    m = aprx.listMaps()[0]
    log(f"  Map: {m.name} ({len(m.listLayers())} layers)")

    log(f"Adding KML directly: {KML_PATH}")
    lyr = m.addDataFromPath(KML_PATH)
    log(f"  addDataFromPath returned: {lyr}")

    if lyr:
        log(f"  Layer name: {lyr.name}")

    aprx.save()
    log("Saved. Open the .aprx in ArcGIS Pro to check if the aerial image appears.")


if __name__ == "__main__":
    main()
