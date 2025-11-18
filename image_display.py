from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np

gdal.UseExceptions()

path = R"C:\Users\HP\Downloads\grupa_13.tif"

dataset: gdal.Dataset = gdal.Open(path)

coastal_blue = dataset.GetRasterBand(1).ReadAsArray()
blue = dataset.GetRasterBand(2).ReadAsArray()
green_i = dataset.GetRasterBand(3).ReadAsArray()
green = dataset.GetRasterBand(4).ReadAsArray()
yellow = dataset.GetRasterBand(5).ReadAsArray()
red = dataset.GetRasterBand(6).ReadAsArray()
red_edge = dataset.GetRasterBand(7).ReadAsArray()
nir = dataset.GetRasterBand(8).ReadAsArray()

rgb = np.dstack((red, green, blue)).astype(np.float64)
min = np.percentile(rgb, 1)
max = np.percentile(rgb, 99.9)
rgb = np.clip((rgb - min) / (max - min), 0, 1)
plt.imshow(rgb)
plt.show()