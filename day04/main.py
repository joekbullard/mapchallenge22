#!/usr/bin/env python

import json

import geopandas as gpd
import numpy as np
import rasterio
from pyproj import CRS
from rasterio.mask import mask
from rasterio.warp import Resampling, calculate_default_transform, reproject
from shapely.geometry import box


def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())["features"][0]["geometry"]]


red_fp = "S2A_MSIL1C_20220807T112131_N0400_R037_T30UVB_20220807T145932.SAFE/GRANULE/L1C_T30UVB_A037214_20220807T112125/IMG_DATA/T30UVB_20220807T112131_B04.jp2"
nir_fp = "S2A_MSIL1C_20220807T112131_N0400_R037_T30UVB_20220807T145932.SAFE/GRANULE/L1C_T30UVB_A037214_20220807T112125/IMG_DATA/T30UVB_20220807T112131_B08.jp2"

red_out_fp = "red_27700.tiff"
nir_out_fp = "nir_27700.tiff"

red_clip = "red_clip.tiff"
nir_clip = "nir_clip.tiff"

rasters = [red_fp, nir_fp]
outputs = [red_out_fp, nir_out_fp]
clips = [red_clip, nir_clip]

dst_crs = "EPSG:27700"


for rast, out in zip(rasters, outputs):
    with rasterio.open(rast, 'r+') as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )

        kwargs = src.meta.copy()
        src.nodata = -9999
        kwargs.update(
            {
                "driver": "GTiff",
                "crs": dst_crs,
                "transform": transform,
                "width": width,
                "height": height,
            }
        )

        print(out)

        with rasterio.open(out, "w", **kwargs) as dst_rst:

            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst_rst, i),
                    # src_transform=srcRst.transform,
                    src_crs=src.crs,
                    # dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest,
                )


clip = gpd.read_file('n_devon_boundary.shp', crs=27700)

for out, clp in zip(outputs, clips):

    with rasterio.open(out) as src:

        clip = clip.to_crs(crs=src.crs.data)
        coords = getFeatures(clip)

        out_img, out_transform = mask(dataset=src, shapes=clip.geometry, crop=True, filled=False)
        out_meta = src.meta.copy()
        epsg_code = int(src.crs.data["init"][5:])

        out_meta.update(
            {
                "driver": "GTiff",
                "height": out_img.shape[1],
                "width": out_img.shape[2],
                "transform": out_transform,
                "crs": CRS.from_epsg(epsg_code).to_proj4(),
            }
        )

        with rasterio.open(clp, "w", **out_meta) as dest:
            dest.write(out_img)


band4 = rasterio.open(red_clip)
band8 = rasterio.open(nir_clip)

red = band4.read(1).astype("float64")
nir = band8.read(1).astype("float64")

ndvi = np.where((nir + red) == 0.0, 0, (nir - red) / (nir + red))
ndvi[:5, :5]


ndviImage = rasterio.open(
    "northdevon_ndvi_2.tiff",
    "w",
    driver="GTiff",
    nodata = -999,
    width=band4.width,
    height=band4.height,
    count=1,
    crs=band4.crs,
    transform=band4.transform,
    dtype="float64",
)

ndviImage.write(ndvi, 1)
ndviImage.close()



with rasterio.open('northdevon_ndvi_2.tiff', 'r+') as src:
    out_img, out_transform = mask(dataset=src, shapes=clip.geometry, crop=True, filled=False)
    out_meta.update(
            {
                "driver": "GTiff",
                "transform": out_transform,
                "crs": CRS.from_epsg(epsg_code).to_proj4(),
            }
        )
    src.write(out_img)
