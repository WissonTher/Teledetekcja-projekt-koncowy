from osgeo import gdal
import numpy as np
import os
from functions.masking import mask_ndvi, mask_cvi

gdal.UseExceptions()

NO_DATA = 0
WATER_THRESHOLD = 1225

path = R"C:\Users\HP\Downloads\grupa_13.tif"
path_no_water = R"C:\Users\HP\Downloads\grupa_13_masked.tif"

# Helper: Improves faster layer reloading.
# if os.path.exists(path_no_water) or os.path.exists(R"C:\Users\HP\Downloads\grupa_13_masked.tif.aux.xml"):
#     os.remove(path_no_water)
#     os.remove(R"C:\Users\HP\Downloads\grupa_13_masked.tif.aux.xml")

dataset: gdal.Dataset = gdal.Open(path)

coastal_blue = dataset.GetRasterBand(1).ReadAsArray().astype(np.float64)
blue = dataset.GetRasterBand(2).ReadAsArray().astype(np.float64)
green_i = dataset.GetRasterBand(3).ReadAsArray().astype(np.float64)
green = dataset.GetRasterBand(4).ReadAsArray().astype(np.float64)
yellow = dataset.GetRasterBand(5).ReadAsArray().astype(np.float64)
red = dataset.GetRasterBand(6).ReadAsArray().astype(np.float64)
red_edge = dataset.GetRasterBand(7).ReadAsArray().astype(np.float64)
nir = dataset.GetRasterBand(8).ReadAsArray().astype(np.float64)

all_bands = [coastal_blue, blue, green_i, green, yellow, red, red_edge, nir]
band_names = ["coastal_blue", "blue", "green_i", "green", "yellow", "red", "red_edge", "nir"]

water_mask = nir <= WATER_THRESHOLD

ndvi_mask = mask_ndvi(nir, red, 0.7)
gndvi_mask = mask_ndvi(nir, green, 0.65)
cvi_mask = mask_cvi(nir, red, green, 3.7)

total_mask = water_mask | cvi_mask | ndvi_mask | gndvi_mask

masked = []
for band in all_bands:
    copy = band.copy()
    copy[total_mask] = NO_DATA
    masked.append(copy.astype(np.uint16))

driver = gdal.GetDriverByName('GTiff')
out_dataset = driver.Create(
    path_no_water,
    dataset.RasterXSize,
    dataset.RasterYSize,
    8,
    gdal.GDT_UInt16
)

for i, (band, name) in enumerate(zip(masked, band_names), start=1):
    out_band = out_dataset.GetRasterBand(i)
    out_band.WriteArray(band)
    out_band.SetNoDataValue(NO_DATA)
    out_band.SetDescription(name)

out_dataset.SetGeoTransform(dataset.GetGeoTransform())
out_dataset.SetProjection(dataset.GetProjection())
out_dataset.FlushCache()
out_dataset = None