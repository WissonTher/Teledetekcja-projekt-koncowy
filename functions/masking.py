import numpy as np

def mask_ndvi(nir_band, red_band, threshold):
    with np.errstate(divide='ignore', invalid='ignore'):
        ndvi = (nir_band - red_band) / (nir_band + red_band)
    mask = ndvi > threshold
    return mask

def mask_cvi(nir_band, red_band, green_band, threshold):
    with np.errstate(divide='ignore', invalid='ignore'):
        ndvi = nir_band * red_band / green_band ** 2
    mask = ndvi > threshold
    return mask