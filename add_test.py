import arcpy
import os
import sys
import shutil
import time

PROJECT_DIR = r"I:\Jobs\20252026\Savio\20260325_Flood_Aerial"
APRX_PATH = os.path.join(PROJECT_DIR, "flood_aerial.aprx")
TEST_KML = r"I:\Raster\October 2022 Flood Imagery_20230517\AIG\1007\2022_10_07_035503_00_00_V_001.kml"
KML_OUTPUT = os.path.join(PROJECT_DIR, "AIG_KML_test")

arcpy.env.overwriteOutput = True


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()


def main():
    log("=== SMOKE TEST: single KML import ===")
    log(f"KML:  {TEST_KML}")
    log(f"APRX: {APRX_PATH}")
    log("")

    if not os.path.exists(TEST_KML):
        log(f"ERROR: KML not found: {TEST_KML}")
        return

    if not os.path.exists(APRX_PATH):
        log(f"ERROR: Project not found: {APRX_PATH}")
        return

    if os.path.exists(KML_OUTPUT):
        shutil.rmtree(KML_OUTPUT)
        log(f"  Cleaned previous output: {KML_OUTPUT}")
    os.makedirs(KML_OUTPUT, exist_ok=True)

    log("Converting KML to layer...")
    try:
        arcpy.conversion.KMLToLayer(TEST_KML, KML_OUTPUT, "test_overlay", "GROUNDOVERLAY")
        log("  KMLToLayer succeeded")
    except Exception as e:
        log(f"  KMLToLayer FAILED: {e}")
        return

    lyrx = os.path.join(KML_OUTPUT, "test_overlay.lyrx")
    if not os.path.exists(lyrx):
        log(f"  WARNING: No .lyrx produced at {lyrx}")
        log("  Listing output folder:")
        for f in os.listdir(KML_OUTPUT):
            log(f"    {f}")
        return

    log(f"  Layer file: {lyrx}")

    log("Opening project...")
    aprx = arcpy.mp.ArcGISProject(APRX_PATH)
    maps = aprx.listMaps()
    if not maps:
        log("  ERROR: No maps in project")
        return

    m = maps[0]
    log(f"  Map: {m.name}")

    log("Adding layer to map...")
    lyr_file = arcpy.mp.LayerFile(lyrx)
    m.addLayer(lyr_file)

    aprx.save()
    log(f"  Saved: {APRX_PATH}")

    log("")
    log("SUCCESS - open the .aprx in ArcGIS Pro and check if the image appears.")


if __name__ == "__main__":
    main()
