import osgb
import requests
import contextily as cx
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import rasterio
from rasterio.plot import show
from rasterio.crs import CRS
from rasterio.mask import mask


df = pd.read_html("https://treksandtors.co/dartmoor-tors/")[0]

new_header = df.iloc[0]
df = df[1:]
df.columns = new_header
df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("(", "")
    .str.replace(")", "")
)

df[["easting", "northing"]] = [osgb.parse_grid(row) for row in df.grid_reference]

gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.easting, df.northing), crs="EPSG:27700"
)
gdf = gdf.to_crs("EPSG:3857")

mask_url = "https://environment.data.gov.uk/arcgis/rest/services/NE/NationalParksEngland/FeatureServer/0/query?where=name+%3D+%27DARTMOOR%27&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&havingClause=&gdbVersion=&historicMoment=&returnDistinctValues=false&returnIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&multipatchOption=xyFootprint&resultOffset=&resultRecordCount=&returnTrueCurves=false&returnExceededLimitFeatures=false&quantizationParameters=&returnCentroid=false&sqlFormat=none&resultType=&featureEncoding=esriDefault&datumTransformation=&f=geojson"
mask_r = requests.get(mask_url)

mask_gdf = gpd.read_file(mask_r.text)
mask_gdf = mask_gdf.to_crs("EPSG:3857")

gdf = gpd.clip(gdf, mask_gdf)

gdf["height_m"] = gdf["height_m"].astype("int64")

west, south, east, north = bbox = mask_gdf.total_bounds

img, ext = cx.bounds2raster(
    west,
    south,
    east,
    north,
    "basemap.tif",
    source=cx.providers.CartoDB.DarkMatterNoLabels,
)


fig, ax = plt.subplots(figsize=(10, 10))

with rasterio.open("basemap.tif") as r:
    out, _ = mask(r, mask_gdf.geometry, invert=False)
    plt.axis("off")
    ax.set_aspect("equal")
    _.crs = CRS.from_epsg(3857)
    ax.set_title(
        "Dartmoor Tors",
        color="black",
        font="monospace",
        fontweight="bold",
        loc="left",
        y=1.0,
        pad=-10,
    )
    rasterio.plot.show(out, ax=ax, transform=_)
    gdf.to_crs(3857).plot(
        ax=ax,
        marker="^",
        column="height_m",
        cmap="viridis",
        legend=True,
        legend_kwds={"label": "height (m)", "shrink": 0.3},
    )
    ax.add_artist(ScaleBar(dx=1, location="lower left"))
    ax.text(
        0.85,
        0.02,
        "Crown copyright and database rights 2022 \nTor data from treksandtors.co.uk",
        font="monospace",
        transform=ax.transAxes,
        fontsize=6,
    )
    plt.savefig("output.png", bbox_inches="tight", pad_inches=0)

    plt.show()
