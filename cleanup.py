import arcpy
import os
import shutil
import time
import sys

PROJECT_DIR = r"I:\Jobs\20252026\Savio\20260325_Flood_Aerial"

TARGETS = [
    os.path.join(PROJECT_DIR, "aig_master.kml"),
    os.path.join(PROJECT_DIR, "AIG_KML"),
    os.path.join(PROJECT_DIR, "AIG_KML_test"),
    os.path.join(PROJECT_DIR, "Wimmera_extracted"),
]

SOURCE = r"I:\Raster\October 2022 Flood Imagery_20230517"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()


def main():
    log("Cleanup: removing resources created by add.py")
    log("")

    for target in TARGETS:
        if not os.path.exists(target):
            log(f"  Not found, skipping: {target}")
            continue

        if target.startswith(SOURCE):
            log(f"  SKIPPED (source data): {target}")
            continue

        try:
            if target.lower().endswith(".gdb"):
                arcpy.management.Delete(target)
            elif os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)
            log(f"  Removed: {target}")
        except Exception as e:
            log(f"  FAILED: {target} - {e}")

    log("")
    log("Done.")


if __name__ == "__main__":
    main()
