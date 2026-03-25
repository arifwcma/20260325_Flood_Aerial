# Missing Resource Sets for `add.py`

These 5 data sets from `I:\Raster\October 2022 Flood Imagery_20230517` are not handled by the current `add.py` script.

---

## 1. Satellite Imagery (ECW Rasters)

- **Source:** `I:\Raster\October 2022 Flood Imagery_20230517\Satellite Imagery\Satellite_Imagery\`
- **Files:** 5 `.ecw` rasters with `.ers` header files
  - `radar_kerang_egeos\kerang-vh_2022nov16_sat_sar_3m_epsg28354.ecw`
  - `radar_kerang_egeos\kerang-vv_2022nov16_sat_sar_3m_epsg28354.ecw`
  - `scc_2022nov23\optical_SPOT\kerang_2022nov18_sat_vis_150cm_epsg32754.ecw`
  - `scc_2022nov23\sar\echuca-shepparton-vh_2022nov18_sat_sar_3m_epsg28354.ecw`
  - `scc_2022nov23\sar\echuca-shepparton-vv_2022nov18_sat_sar_3m_epsg28354.ecw`
- **Format:** Fully georeferenced ECW + ERS, CRS is MGA54 (EPSG:28354) and UTM54S (EPSG:32754)
- **Action:** Add each `.ecw` as a raster layer via `addDataFromPath`, or create a mosaic dataset. No conversion needed.

---

## 2. FireMapper (Geotagged Photos)

- **Source:** `I:\Raster\October 2022 Flood Imagery_20230517\FireMapper\`
- **Files:** 5,897 JPGs across 71 date subfolders (`{month}\{day}\*.jpg`)
- **Format:** Plain JPGs with no sidecar georeferencing files. May have EXIF GPS tags embedded.
- **Action:** Use `arcpy.management.GeoTaggedPhotosToPoints()` to extract EXIF GPS and create a point feature class with photo links.

---

## 3. File Geodatabases (CMA Feature Classes)

- **Source (root-level):** `I:\Raster\October 2022 Flood Imagery_20230517\CMA_Imagery_Request_Oct_2022_Floods.gdb`
- **Source (CMA subfolder):** `I:\Raster\October 2022 Flood Imagery_20230517\October 2022 Floods Imagery Request for CMA\CMA_Imagery_Request_Oct_2022_Floods.gdb`
- **Format:** File Geodatabases with ~20+ feature classes (likely vector layers with spatial data)
- **Action:** List feature classes with `arcpy.ListFeatureClasses()`, then add each to the map via `addDataFromPath`. These may be duplicates of each other — compare before adding both.

---

## 4. SnapSendSolve (CSV with Coordinates)

- **Source:** `I:\Raster\October 2022 Flood Imagery_20230517\SnapSendSolve\SSS_Oct_2022_Flood_Event_All.csv`
- **Format:** CSV, likely with latitude/longitude columns (WGS84)
- **Action:** Use `arcpy.management.XYTableToPoint()` to create a point feature class. Inspect column names first to determine the X/Y field names.

---

## 5. Wimmera (Spreadsheets + Zipped GDB)

- **Source:** `I:\Raster\October 2022 Flood Imagery_20230517\Wimmera\`
- **Files:**
  - `Wimmera.gdb.zip` — compressed File Geodatabase (needs extracting first)
  - `AIG_Wimmera.xls` / `.xlsx` — may contain coordinate columns
  - `FireMapper_Wimmera.xls` — may contain coordinate columns
  - `SSS_Wimmera.xls` — may contain coordinate columns
- **Action:** Extract the `.gdb.zip`, add GDB feature classes to map. For spreadsheets, inspect for lat/lon columns and use `XYTableToPoint` if present; otherwise add as standalone tables.
