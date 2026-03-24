import arcpy
import os
import sys
import shutil
import time
import traceback
import xml.etree.ElementTree as ET

SOURCE = r"I:\Raster\October 2022 Flood Imagery_20230517"
PROJECT_DIR = r"I:\Jobs\20252026\Savio\20260325_Flood_Aerial"
GDB_NAME = "FloodAerial.gdb"
GDB = os.path.join(PROJECT_DIR, GDB_NAME)
APRX_PATH = os.path.join(PROJECT_DIR, "FloodAerial.aprx")
SR = arcpy.SpatialReference(28354)

arcpy.env.overwriteOutput = True
summary = {}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()


def create_gdb():
    log("Creating file geodatabase...")
    if arcpy.Exists(GDB):
        log(f"  Already exists, skipping")
        return
    arcpy.management.CreateFileGDB(PROJECT_DIR, GDB_NAME)
    log(f"  Done: {GDB}")


def create_mosaic(name, input_paths, raster_filter=None, recurse=False):
    mosaic = os.path.join(GDB, name)

    if not arcpy.Exists(mosaic):
        arcpy.management.CreateMosaicDataset(GDB, name, SR)
        log(f"  Created mosaic dataset: {name}")

    sub = "SUBFOLDERS" if recurse else "NO_SUBFOLDERS"
    log(f"  Adding rasters (filter={raster_filter or 'all'}, recurse={recurse})...")
    log(f"  This may take a while on a network drive...")

    kwargs = {
        "in_mosaic_dataset": mosaic,
        "raster_type": "Raster Dataset",
        "input_path": input_paths,
        "sub_folder": sub,
        "update_cellsize_ranges": "UPDATE_CELL_SIZES",
        "update_boundary": "UPDATE_BOUNDARY",
        "update_overviews": "NO_OVERVIEWS",
        "duplicate_items_action": "OVERWRITE_DUPLICATES",
    }
    if raster_filter:
        kwargs["filter"] = raster_filter

    arcpy.management.AddRastersToMosaicDataset(**kwargs)

    count = int(arcpy.management.GetCount(mosaic)[0])
    log(f"  Mosaic '{name}': {count} rasters")
    return mosaic, count


def build_master_kml(kml_files, output_path):
    KNS = "{http://www.opengis.net/kml/2.2}"
    ET.register_namespace("", "http://www.opengis.net/kml/2.2")
    ET.register_namespace("gx", "http://www.google.com/kml/ext/2.2")

    root = ET.Element(f"{KNS}kml")
    doc = ET.SubElement(root, f"{KNS}Document")
    name_el = ET.SubElement(doc, f"{KNS}name")
    name_el.text = "AIG Aerial Photos"

    count = 0
    for kml_path in kml_files:
        kml_dir = os.path.dirname(kml_path)
        try:
            tree = ET.parse(kml_path)
        except ET.ParseError:
            continue
        for overlay in tree.iter(f"{KNS}GroundOverlay"):
            href_el = overlay.find(f"{KNS}Icon/{KNS}href")
            if href_el is None or not href_el.text:
                continue
            jpg_path = os.path.join(kml_dir, href_el.text.strip())
            if not os.path.isfile(jpg_path):
                continue
            href_el.text = jpg_path
            doc.append(overlay)
            count += 1

    out_tree = ET.ElementTree(root)
    try:
        ET.indent(out_tree)
    except AttributeError:
        pass
    out_tree.write(output_path, xml_declaration=True, encoding="utf-8")
    return count


def process_aig():
    log("")
    log("=" * 50)
    log("AIG AERIAL PHOTOS")
    log("=" * 50)

    aig_dir = os.path.join(SOURCE, "AIG")
    kml_lyrx = None
    points_path = None

    log("Scanning AIG folders for KML files...")
    kml_files = []
    folders = sorted(
        d for d in os.listdir(aig_dir)
        if os.path.isdir(os.path.join(aig_dir, d))
    )
    for i, folder in enumerate(folders):
        fp = os.path.join(aig_dir, folder)
        for f in os.listdir(fp):
            if f.lower().endswith(".kml"):
                kml_files.append(os.path.join(fp, f))
        if (i + 1) % 20 == 0:
            log(f"  Scanned {i + 1}/{len(folders)} folders...")
    log(f"  Found {len(kml_files)} KML files across {len(folders)} folders")

    if kml_files:
        master_kml = os.path.join(PROJECT_DIR, "aig_master.kml")
        log("Building master KML with absolute image paths...")
        overlay_count = build_master_kml(kml_files, master_kml)
        log(f"  {overlay_count} ground overlays written to master KML")
        summary["AIG Ground Overlays (KML)"] = overlay_count

        if overlay_count > 0:
            kml_output = os.path.join(PROJECT_DIR, "AIG_KML")
            os.makedirs(kml_output, exist_ok=True)
            log("Converting master KML to layer (this may take a long time)...")
            try:
                arcpy.conversion.KMLToLayer(
                    master_kml, kml_output, "AIG_Aerial",
                    "GROUNDOVERLAY"
                )
                lyrx_path = os.path.join(kml_output, "AIG_Aerial.lyrx")
                if os.path.exists(lyrx_path):
                    kml_lyrx = lyrx_path
                    log(f"  Done: {kml_lyrx}")
                else:
                    log("  WARNING: No .lyrx produced (gx:LatLonQuad may not be supported)")
            except Exception as e:
                log(f"  FAILED: {e}")
                summary["AIG KML Import"] = "FAILED"

    log("Scanning for EO_POINTS shapefiles...")
    shps = []
    for i, folder in enumerate(folders):
        fp = os.path.join(aig_dir, folder)
        for f in os.listdir(fp):
            if f.lower().endswith(".shp") and "eo_points" in f.lower():
                shps.append(os.path.join(fp, f))
        if (i + 1) % 20 == 0:
            log(f"  Scanned {i + 1}/{len(folders)} folders...")

    log(f"  Found {len(shps)} shapefiles across {len(folders)} folders")

    if shps:
        points_path = os.path.join(GDB, "AIG_Photo_Locations")
        try:
            log("  Merging shapefiles...")
            arcpy.management.Merge(shps, points_path)
            count = int(arcpy.management.GetCount(points_path)[0])
            log(f"  Done: {count} photo location points")
            summary["AIG Photo Locations"] = count
        except Exception as e:
            log(f"  FAILED: {e}")
            summary["AIG Photo Locations"] = "FAILED"
            points_path = None

    return kml_lyrx, points_path


def process_linescans():
    log("")
    log("=" * 50)
    log("LINESCANS")
    log("=" * 50)

    linescans_dir = os.path.join(SOURCE, "Linescans")
    rgb_folders = []
    other_folders = []

    log("Scanning for geocorrected folders...")
    for root, dirs, files in os.walk(linescans_dir):
        if os.path.basename(root).lower() != "geocorrected":
            continue
        parent = os.path.basename(os.path.dirname(root))
        if "_rgb_" in parent.lower():
            rgb_folders.append(root)
            log(f"  RGB: {parent}")
        else:
            other_folders.append(root)
            log(f"  Non-RGB: {parent}")

    rgb_mosaic = None
    other_mosaic = None

    if rgb_folders:
        log(f"Building RGB linescan mosaic ({len(rgb_folders)} folders)...")
        try:
            rgb_mosaic, count = create_mosaic(
                "Linescans_RGB", ";".join(rgb_folders), "*.jpg", False
            )
            summary["Linescans RGB"] = count
        except Exception as e:
            log(f"  FAILED: {e}")
            summary["Linescans RGB"] = "FAILED"

    if other_folders:
        log(f"Building non-RGB linescan mosaic ({len(other_folders)} folders)...")
        try:
            other_mosaic, count = create_mosaic(
                "Linescans_NonRGB", ";".join(other_folders), None, False
            )
            summary["Linescans Non-RGB"] = count
        except Exception as e:
            log(f"  FAILED: {e}")
            summary["Linescans Non-RGB"] = "FAILED"

    return rgb_mosaic, other_mosaic


def find_template():
    pro_dir = arcpy.GetInstallInfo()["InstallDir"]
    log(f"  Pro install: {pro_dir}")

    for root, dirs, files in os.walk(os.path.join(pro_dir, "Resources")):
        for f in files:
            if f.lower().endswith(".aprx"):
                return os.path.join(root, f)

    fallback = os.path.join(
        SOURCE,
        "October 2022 Floods Imagery Request for CMA",
        "October 2022 Floods Imagery Request for CMA.aprx",
    )
    if os.path.exists(fallback):
        return fallback

    return None


def setup_project(aig_mosaic, aig_points, rgb_mosaic, other_mosaic):
    log("")
    log("=" * 50)
    log("PROJECT SETUP")
    log("=" * 50)

    if not os.path.exists(APRX_PATH):
        log("Looking for .aprx template...")
        template = find_template()
        if not template:
            log("  ERROR: No .aprx template found")
            log(f"  Create a project manually and add data from: {GDB}")
            return
        shutil.copy2(template, APRX_PATH)
        log(f"  Created from: {template}")
    else:
        log(f"Using existing: {APRX_PATH}")

    aprx = arcpy.mp.ArcGISProject(APRX_PATH)
    maps = aprx.listMaps()
    if not maps:
        log("  ERROR: No maps in project file")
        aprx.save()
        return

    m = maps[0]
    log(f"  Map: {m.name}")

    for lyr in m.listLayers():
        try:
            m.removeLayer(lyr)
        except Exception:
            pass

    m.spatialReference = SR
    log("  CRS set to GDA94 / MGA zone 54 (EPSG:28354)")

    try:
        m.addBasemap("Imagery")
        log("  Basemap: Imagery")
    except Exception:
        try:
            m.addBasemap("Topographic")
            log("  Basemap: Topographic")
        except Exception:
            log("  WARNING: Could not add basemap")

    layer_groups = [
        ("AIG Aerial Photos", [
            (aig_mosaic, "AIG Aerial Overlays"),
            (aig_points, "AIG Photo Locations"),
        ]),
        ("Linescans", [
            (rgb_mosaic, "RGB Linescans"),
            (other_mosaic, "Non-RGB Linescans"),
        ]),
    ]

    def layer_exists(p):
        if p is None:
            return False
        if p.lower().endswith(".lyrx"):
            return os.path.exists(p)
        return arcpy.Exists(p)

    can_group = hasattr(m, "createGroupLayer")
    if not can_group:
        log("  Group layers not supported in this version, adding flat")

    for group_name, layers in layer_groups:
        valid = [(p, n) for p, n in layers if layer_exists(p)]
        if not valid:
            continue

        grp = None
        if can_group:
            try:
                grp = m.createGroupLayer(group_name)
                log(f"  Group: {group_name}")
            except Exception as e:
                log(f"  Could not create group '{group_name}': {e}")
                can_group = False

        for data_path, label in valid:
            try:
                if data_path.lower().endswith(".lyrx"):
                    lyr_file = arcpy.mp.LayerFile(data_path)
                    if grp:
                        m.addLayerToGroup(grp, lyr_file)
                    else:
                        m.addLayer(lyr_file)
                else:
                    lyr = m.addDataFromPath(data_path)
                    if lyr:
                        lyr.name = label
                    if grp and lyr:
                        m.addLayerToGroup(grp, lyr)
                        m.removeLayer(lyr)
                log(f"    + {label}")
            except Exception as e:
                log(f"    FAILED ({label}): {e}")

    aprx.save()
    log(f"  Saved: {APRX_PATH}")


def main():
    t0 = time.time()

    log("=" * 60)
    log("  FLOOD AERIAL IMAGERY - ArcGIS Pro Project Builder")
    log("=" * 60)
    log(f"Source:  {SOURCE}")
    log(f"Output:  {PROJECT_DIR}")
    log("")

    try:
        create_gdb()
        aig_mosaic, aig_points = process_aig()
        rgb_mosaic, other_mosaic = process_linescans()
        setup_project(aig_mosaic, aig_points, rgb_mosaic, other_mosaic)
    except Exception:
        log("FATAL ERROR:")
        traceback.print_exc()

    elapsed = time.time() - t0

    log("")
    log("=" * 60)
    log("  IMPORT SUMMARY")
    log("=" * 60)
    for cat, count in summary.items():
        log(f"  {cat:.<40s} {count}")
    log(f"  {'Elapsed':.<40s} {elapsed:.0f}s ({elapsed / 60:.1f} min)")
    log("=" * 60)
    if os.path.exists(APRX_PATH):
        log(f"\nOpen in ArcGIS Pro: {APRX_PATH}")


if __name__ == "__main__":
    main()
