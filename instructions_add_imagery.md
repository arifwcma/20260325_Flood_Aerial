# Instructions: Adding Flood Imagery to ArcGIS Pro

**Project:** `I:\Jobs\20252026\Savio\20260325_Flood_Aerial\flood_imagery.aprx`
**Source data:** `I:\Raster\October 2022 Flood Imagery_20230517`

---

## Inventory Summary

| Source Folder | Content | Count | Georeferenced? |
|---|---|---|---|
| AIG | Aerial JPGs from FB300 airborne camera | 12,376 images across 74 date folders | Via KML/TXT sidecars only |
| AIG | EO_POINTS shapefiles (camera target points) | ~393 shapefiles across date folders | Yes (SHP + PRJ) |
| FireMapper | JPGs from FireMapper iPad app | 5,897 images across 71 date folders | No sidecar files; may have EXIF GPS |
| Linescans | Geocorrected BSQ rasters (thermal + RGB) | 38 geocorrected sets across 3 dates | Yes (JGW + PRJ, MGA94 Zone 54) |
| Linescans | Quickprint JPGs | 38 quickprint JPGs | No |
| Satellite Imagery | 5 ECW rasters (SAR radar + SPOT optical) | 2.7 GB total | Yes (ECW + ERS headers, MGA54 / UTM54S) |
| SnapSendSolve | CSV of flood reports | 1 CSV file | Likely has lat/lon columns |
| Wimmera | Spreadsheets + Wimmera.gdb.zip | 4 XLS/XLSX + 1 GDB zip | GDB likely has spatial data |
| CMA_Imagery_Request_Oct_2022_Floods.gdb | File Geodatabase (root level) | ~20+ feature classes | Yes |
| October 2022 Floods Imagery Request for CMA | Existing ArcGIS Pro project + GDB | 1 APRX + 1 GDB + spreadsheets | Yes |

---

## Step-by-Step Instructions

### STEP 0 — Reference the Existing Project

- Before building from scratch, open the existing project at:
  `I:\Raster\October 2022 Flood Imagery_20230517\October 2022 Floods Imagery Request for CMA\October 2022 Floods Imagery Request for CMA.aprx`
- This was prepared earlier and already references the CMA GDB. Inspect what layers and data it contains — it may save you significant setup work.

---

### STEP 1 — Add the File Geodatabases

These are the easiest and most reliable data sources:

- **Add the root-level GDB as a project database connection:**
  `I:\Raster\October 2022 Flood Imagery_20230517\CMA_Imagery_Request_Oct_2022_Floods.gdb`
  → Right-click "Databases" in Catalog > "Add Database" > browse to the .gdb folder
  → Then drag the feature classes you need from the GDB into your map

- **Also consider the CMA subfolder GDB:**
  `I:\Raster\October 2022 Flood Imagery_20230517\October 2022 Floods Imagery Request for CMA\CMA_Imagery_Request_Oct_2022_Floods.gdb`
  → This may be a duplicate or an updated version of the root-level GDB. Compare both.

- **Extract and add the Wimmera GDB:**
  → Unzip `I:\Raster\October 2022 Flood Imagery_20230517\Wimmera\Wimmera.gdb.zip`
  → Add the resulting .gdb as another database connection

---

### STEP 2 — Add the Linescans (Georeferenced Rasters)

These are the only imagery that are **properly georeferenced out of the box**:

- Navigate to the `geocorrected` subfolders under each linescan location:
  `I:\Raster\October 2022 Flood Imagery_20230517\Linescans\{date}\{location}\geocorrected\`
- Dates: `10_14`, `10_16`, `10_17`
- Locations include: HORSHAM, DOOEN, LAKETAYLOR, LONGERENONG, MCKENZIECREEK, MURTOA, STAWELL, WONWANDAH, NATIMUK, PINELAKE, QUANTONG, RUPANYUP
- Each geocorrected folder has both a **thermal (grayscale) BSQ** and an **RGB BSQ** version
- **Add the `.bsq` files directly** — ArcGIS will read the `.hdr`, `.jgw`, and `.prj` sidecars automatically
- Alternatively, add the `.jpg` files from geocorrected folders (they have `.jgw` world files too)
- Coordinate system: **MGA94 Zone 54** (GDA94 / MGA zone 54, EPSG:28354)
- There are **38 geocorrected raster sets** in total (19 locations x 2 variants: thermal + RGB)
- Skip the `quickprint` subfolders — those are non-georeferenced simple JPG previews

---

### STEP 3 — Add the AIG Aerial Imagery via KML-to-Layer Conversion

The AIG images (12,376 JPGs across 74 date folders) are **not directly georeferenced** but each has a companion `.kml` file containing a `GroundOverlay` with 4-corner coordinates.

**Option A — KML to Layer (Recommended for ArcGIS Pro):**
- Use the **KML To Layer** geoprocessing tool (Conversion Tools > From KML)
- Process each date folder's KML files, or batch-process all
- Input: the individual `.kml` files from `I:\Raster\October 2022 Flood Imagery_20230517\AIG\{date}\*.kml`
- This will create feature layers with the image footprints and embedded raster references
- **Important:** The KMLs reference JPGs using relative paths — the `.kml` and `.jpg` files must stay in the same folder

**Option B — Georeference using TXT GCPs (Advanced):**
- Each `.txt` sidecar has 12 Ground Control Points with pixel X,Y → lat/lon mappings
- You could batch-georeference the JPGs using a Python/arcpy script that reads the TXT files and applies the GCPs
- This produces properly warped rasters but is significantly more work

**Also add the EO_POINTS shapefiles:**
- Each AIG date folder contains `EO_POINTS_*.shp` shapefiles
- These are point features marking where the camera was aimed (track/target points)
- Add these as vector layers — they give you a spatial index of where images were captured
- ~393 shapefiles total; consider merging them into a single feature class using the **Merge** tool

---

### STEP 4 — Add the FireMapper Imagery

- Location: `I:\Raster\October 2022 Flood Imagery_20230517\FireMapper\{month}\{day}\*.jpg`
- 5,897 JPG images across 71 date subfolders (Oct 9 to Dec 31)
- **These have NO georeferencing sidecar files** (no KML, no JGW, no world file, no XML)
- They may contain **EXIF GPS tags** embedded in the JPEG metadata
- **To use in ArcGIS Pro:**
  → Use the **GeoTagged Photos To Points** geoprocessing tool (Data Management > Photos)
  → Point it at the FireMapper folder (recurse subfolders)
  → This will extract EXIF GPS coordinates and create a point feature class
  → Each point will have an attachment or path link to the original photo
- The images will NOT display as raster overlays — they will appear as geolocated photo points
- If EXIF GPS is missing from some/all, these images cannot be spatially placed without manual effort

---

### STEP 5 — Add the SnapSendSolve CSV

- File: `I:\Raster\October 2022 Flood Imagery_20230517\SnapSendSolve\SSS_Oct_2022_Flood_Event_All.csv`
- This likely contains crowd-sourced flood reports with latitude/longitude columns
- **To add:** Use the **XY Table To Point** geoprocessing tool, or add it as a table and use "Display XY Data"
- Check the column names for the coordinate fields (likely `Latitude`/`Longitude` or similar)
- Coordinate system will likely be **GCS WGS84 (EPSG:4326)**

---

### STEP 6 — Add the Satellite Imagery (ECW Rasters)

Extracted to: `I:\Raster\October 2022 Flood Imagery_20230517\Satellite Imagery\Satellite_Imagery\`

5 fully georeferenced ECW rasters across two areas:

**Kerang area (16-18 Nov 2022):**
- `radar_kerang_egeos\kerang-vh_2022nov16_sat_sar_3m_epsg28354.ecw` — SAR VH polarisation, ~1.3m, GDA94/MGA54 (461 MB)
- `radar_kerang_egeos\kerang-vv_2022nov16_sat_sar_3m_epsg28354.ecw` — SAR VV polarisation, ~1.2m, GDA94/MGA54 (456 MB)
- `scc_2022nov23\optical_SPOT\kerang_2022nov18_sat_vis_150cm_epsg32754.ecw` — SPOT optical 4-band, 1.5m, WGS84/UTM54S (276 MB)

**Echuca-Shepparton area (18 Nov 2022):**
- `scc_2022nov23\sar\echuca-shepparton-vh_2022nov18_sat_sar_3m_epsg28354.ecw` — SAR VH, ~1.3m, GDA94/MGA54 (814 MB)
- `scc_2022nov23\sar\echuca-shepparton-vv_2022nov18_sat_sar_3m_epsg28354.ecw` — SAR VV, ~1.2m, GDA94/MGA54 (758 MB)

- **Drag the `.ecw` files directly into the map** — ArcGIS reads ECW natively with the `.ers` header files
- No conversion or georeferencing needed
- SAR VH polarisation is best for detecting standing water/flooding; VV shows surface roughness

---

### STEP 7 — Add the Wimmera Spreadsheets (Reference Data)

- Location: `I:\Raster\October 2022 Flood Imagery_20230517\Wimmera\`
- Files: `AIG_Wimmera.xls`, `AIG_Wimmera.xlsx`, `FireMapper_Wimmera.xls`, `SSS_Wimmera.xls`
- These appear to be filtered/regional subsets of the imagery metadata for the Wimmera CMA
- Add as standalone tables or use XY Table To Point if they contain coordinate columns
- The `Wimmera.gdb.zip` was covered in Step 1

---

### STEP 8 — Add the CMA Spreadsheets

- File: `I:\Raster\October 2022 Flood Imagery_20230517\October 2022 Floods Imagery Request for CMA\Spreadsheets for each CMA\SSS_20221015_to_20221027.csv`
- Add as a table; use XY Table To Point if it has coordinate columns

---

## Recommended Layer Organisation in the Map

Organise layers into **Group Layers** for clarity:

- **Linescans_Geocorrected** — all BSQ/JPG rasters from Step 2
- **AIG_Aerial_Overlays** — KML-converted imagery from Step 3
- **AIG_EO_Points** — merged EO_POINTS shapefiles from Step 3
- **FireMapper_Photos** — geotagged photo points from Step 4
- **SnapSendSolve_Reports** — point layer from CSV (Step 5)
- **Satellite_Imagery** — extracted rasters from Step 6
- **CMA_GDB_Layers** — feature classes from the File Geodatabases (Step 1)
- **Reference_Tables** — Wimmera spreadsheets, CMA spreadsheets

---

## Coordinate System Recommendation

- Set the map's coordinate system to **GDA94 / MGA zone 55 (EPSG:28355)** or **GDA2020 / MGA zone 55 (EPSG:7855)** depending on your organisation's standard, since most of Victoria falls in zone 55.
- The Linescans use MGA zone 54 (western Vic) — ArcGIS will reproject on-the-fly.
- The KML/GPS data uses WGS84 geographic coordinates — ArcGIS will also reproject these automatically.
