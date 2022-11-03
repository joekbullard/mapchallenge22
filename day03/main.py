import numpy as np
import requests
import geopandas as gpd
import matplotlib.pyplot as plt
from geovoronoi.plotting import subplot_for_map, plot_voronoi_polys_with_points_in_area
from geovoronoi import voronoi_regions_from_coords

allotment_url = "https://opendata.bristol.gov.uk/api/v2/catalog/datasets/allotment-sites/exports/geojson?limit=-1&offset=0&timezone=UTC"
allotment_r = requests.get(allotment_url)

boundary_url = "https://opendata.bristol.gov.uk/api/v2/catalog/datasets/bristol/exports/geojson?limit=-1&offset=0&timezone=UTC"
boundary_r = requests.get(boundary_url)

gdf = gpd.read_file(allotment_r.text)
gdf = gdf.to_crs(27700).centroid
boundary = gpd.read_file(boundary_r.text)

gdf = gdf.to_crs(3395)
boundary = boundary.to_crs(gdf.crs)

area_shape = boundary.iloc[0].geometry

region_polys, region_pts = voronoi_regions_from_coords(gdf, area_shape)




plt.rcParams.update(
    {
        "figure.facecolor": "black",
        "text.color": "white",
        "font.family": "monospace",
        "font.weight": "bold",
        "font.size": 20,
    }
)

fig, ax = plt.subplots(figsize=(20, 20))
ax.set_aspect("equal")
plot_voronoi_polys_with_points_in_area(ax, area_shape, region_polys, gdf, region_pts)
gdf.centroid.plot(ax=ax, marker=".", color="black")
plt.axis("off")
plt.figtext(0.9, 0.1, "Bristol Open Data 2022", ha="right", fontsize=12)
plt.figtext(
    0.1,
    0.1,
    """
    Voronoi plots partition geographic areas into regions based 
    on proximity to a closest point. In this example using Bristol allotments, 
    each point (also known as seed) has a related polygon (cell) indicating 
    the geographic area closer to that point than any other
    """,
    ha="left",
    fontsize=12,
)
ax.set_title(
    "Bristol - Distance from nearest allotment",
    color="white",
    font="monospace",
    fontweight="bold",
    loc="center",
    fontsize=20,
    y=0.98,
)
plt.savefig("output.png", bbox_inches="tight", pad_inches=0)
plt.show()
