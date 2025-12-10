import numpy as np
from scipy import ndimage
from skimage.transform import hough_line, hough_circle, hough_circle_peaks
from skimage.filters import gaussian
import matplotlib.pyplot as plt
from osgeo import gdal

#STAŁE
NO_DATA = 0
SINGLE_THRESHOLD = 0.20
HOUGH_CIRCLE_THRESHOLD = 0.10

def przygotowanie_obrazu(bands, total_mask):
    """
    Wygładzanie Gaussa, maskowanie i normalizacja (do 0-1) - tylko red.
    """
    obraz = bands.get("red").copy()

    # Wygładzanie Gaussa (potrzebne do redukcji szumu!)
    obraz_wygładzony = gaussian(obraz, sigma=1.0)

    # Zastosowanie maski (piksele maskowane na 0)
    obraz_wygładzony[total_mask] = NO_DATA

    # Normalizacja do zakresu 0-1 - dla progowania
    obraz_norm = obraz_wygładzony.copy()
    valid_pixels = obraz_norm[obraz_norm > NO_DATA]

    if valid_pixels.size > 0:
        min_val = valid_pixels.min()
        max_val = valid_pixels.max()
        if max_val > min_val:
            obraz_norm[obraz_norm > NO_DATA] = (obraz_norm[obraz_norm > NO_DATA] - min_val) / (max_val - min_val)

    return obraz_norm

def simple_thresholding(image, threshold):
    """
    Proste progowanie zastosowane do siły gradientu, jak to już wcześniej było w Sobelu, ale rozdzielone
    """
    edges = np.zeros_like(image, dtype=np.uint8)
    edges[image >= threshold] = 255
    return edges

def sobel_i_hough(obraz_norm):
    """
     Sobel + Proste Progowanie + Hough
    """
    sobel_x = ndimage.sobel(obraz_norm, axis=1)
    sobel_y = ndimage.sobel(obraz_norm, axis=0)

    # Magnitude Gradientu
    gradient_mag = np.hypot(sobel_x, sobel_y)

    # Normalizacja Magnitude (dla Progowania)
    if gradient_mag.max() > 0:
        gradient_mag_norm = gradient_mag / gradient_mag.max()
    else:
        gradient_mag_norm = np.zeros_like(gradient_mag)

    # Proste Progowanie
    # Krawędzie daej są grube, ponieważ Sobel wykrywa krawędź na kilku pikselach - JAK ZMNIEJSZYĆ KRAWĘDZIE!
    edges_final = simple_thresholding(gradient_mag_norm, SINGLE_THRESHOLD)

    # Transformacja Hougha (Detekcja Geometrii)
    # Ze względu na grube krawędzie, Hough prawdopodobnie będzie generował wiele fałszywych pozytywów...
    # 1. Detekcja Dróg
    h_space_lines, angle_lines, dist_lines = hough_line(edges_final)

    # 2. Detekcja Rond
    min_radius = 5
    max_radius = 50
    hough_radii = np.arange(min_radius, max_radius)
    h_circles = hough_circle(edges_final, hough_radii)

    threshold_value = int(h_circles.max() * HOUGH_CIRCLE_THRESHOLD)

    # hough_circle_peaks domyślnie zwraca lokalne maksima. Aby zwrócić *wszystkie* # potencjalne piki powyżej progu (co jest najbliższe intencji "wykryć wszystkie"),
    # ustawiam total_num_peaks na nieskończoność (np. bardzo dużą liczbę)

    accum, cx, cy, radii = hough_circle_peaks(
        h_circles,
        hough_radii,
        threshold=threshold_value,
        total_num_peaks=np.inf
    )

    return edges_final, h_space_lines, accum, cx, cy, radii


""" if __name__ == '__main__':
    sciezka_do_rastra = R"C:\Users\HP\izabe\Downloads\grupa_13.tif"

    bands_data = wczytaj_pasma(sciezka_do_rastra)

    if bands_data and all(band in bands_data for band in ["nir", "red", "green"]):
        nir_band = bands_data["nir"]
        red_band = bands_data["red"]
        green_band = bands_data["green"]


        # Przygotowanie obrazu
        maska = stworz_maske_wstepna(nir_band, red_band, green_band)
        obraz_do_analyzy = przygotuj_obraz_do_sobela(bands_data, maska)

        # Detekcja krawędzi i ekstrakcja cech
        edges_final, h_space_lines, accum_circles, cx, cy, radii = sobel_no_nms_hough_all_circles(obraz_do_analyzy)

        print(f"Detekcja geometrii zakończona (Wykryto {len(cx)} okręgów powyżej progu {HOUGH_CIRCLE_THRESHOLD * 100}%).")

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        axes[0].imshow(obraz_do_analyzy, cmap='gray')
        axes[0].set_title('1. Zamaskowane i znormalizowane pasmo RED')

        # Krawędzie (Sobel + Proste Progowanie)
        axes[1].imshow(edges_final, cmap='gray')
        axes[1].set_title(f'2. Krawędzie (Brak NMS)')

        # Nałożenie wykrytych okręgów na krawędzie
        axes[2].imshow(edges_final, cmap='gray')
        axes[2].plot(cx, cy, 'o', color='red', markersize=3, label='Wykryte centra rond')
        for center_y, center_x, radius in zip(cy, cx, radii):
             circle = plt.Circle((center_x, center_y), radius, color='red', fill=False, linewidth=1)
             axes[2].add_patch(circle)

        axes[2].set_title(f'3. Wykryte Okręgi (Wszystkie > {HOUGH_CIRCLE_THRESHOLD * 100}%)')

        for ax in axes:
            ax.axis('off')

        plt.show() """
