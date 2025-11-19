from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np
import os

gdal.UseExceptions()

# MODES: NDVI, GNDVI, NIR, CVI
MODE = 'NIR'
LIM = False

NO_DATA = 0
WATER_THRESHOLD = 1225

path = R"C:\Users\HP\Downloads\grupa_13.tif"

dataset: gdal.Dataset = gdal.Open(path)

coastal_blue = dataset.GetRasterBand(1).ReadAsArray().astype(np.float64)
blue = dataset.GetRasterBand(2).ReadAsArray().astype(np.float64)
green_i = dataset.GetRasterBand(3).ReadAsArray().astype(np.float64)
green = dataset.GetRasterBand(4).ReadAsArray().astype(np.float64)
yellow = dataset.GetRasterBand(5).ReadAsArray().astype(np.float64)
red = dataset.GetRasterBand(6).ReadAsArray().astype(np.float64)
red_edge = dataset.GetRasterBand(7).ReadAsArray().astype(np.float64)
nir = dataset.GetRasterBand(8).ReadAsArray().astype(np.float64)

if LIM:
    plt.xlim(1700, 2300)
    plt.ylim(1800, 1300)
else:
    plt.figure(figsize=(18,3))

if MODE == 'NDVI':
    with np.errstate(divide='ignore', invalid='ignore'):
        ndvi = (nir - red) / (nir + red)
    ndvi = np.where(ndvi > 0.7, np.nan, ndvi)
    ndvi = np.ma.masked_invalid(ndvi)
    plt.imshow(ndvi, cmap='RdYlGn')
    if not LIM:
        plt.colorbar(label="NDVI")

elif MODE == 'GNDVI':
    with np.errstate(divide='ignore', invalid='ignore'):
        gndvi = (nir - green) / (nir + green)
    # gndvi = np.where(gndvi > 0.65, np.nan, gndvi)
    gndvi = np.ma.masked_invalid(gndvi)
    plt.imshow(gndvi, cmap='RdYlGn')
    if not LIM:
        plt.colorbar(label="GNDVI")

elif MODE == 'NIR':
    nir = np.ma.masked_equal(nir, 0.0)
    nir = np.where(nir < 1225, np.nan, nir)
    plt.imshow(nir, cmap='GnBu_r', vmin=200)
    plt.colorbar(label="NIR")

elif MODE == 'CVI':
    with np.errstate(divide='ignore', invalid='ignore'):
        chlorophyll = nir * red / green**2
    chlorophyll = np.where(chlorophyll > 3.5, np.nan, chlorophyll)
    chlorophyll = np.ma.masked_invalid(chlorophyll)
    plt.imshow(chlorophyll, cmap='viridis', vmin=0, vmax=7)
    if not LIM:
        plt.colorbar(label="CVI")

plt.show()
