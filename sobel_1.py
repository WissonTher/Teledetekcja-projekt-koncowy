"""
Moduł do detekcji krawędzi dróg metodą Sobela
Projekt: Teledetekcja - detekcja obiektów
Autorzy: Izabela Sobka, Szymon Węgliński
"""

import numpy as np
from osgeo import gdal
from scipy import ndimage


def wczytaj_raster(sciezka):
    """
    Wczytuje raster z pliku.
    Args:
        sciezka (str): Ścieżka do pliku rastrowego
    Returns:
        numpy.ndarray: Tablica z danymi rastra (kanał 1) lub None w razie błędu
    """
    try:
        dataset = gdal.Open(sciezka)
        if dataset is None:
            print(
                f"Błąd: Nie można otworzyć pliku {sciezka}"
            )  # sorry akurat w tym temacie nie wiem skąd zaczerpniemy ścieżkę, czy rep stoi u ciebie?
            return None

        band = dataset.GetRasterBand(1)
        raster = band.ReadAsArray()

        dataset = None
        return raster
    except Exception as e:
        print(f"Błąd podczas wczytywania rastra: {e}")
        return None


def sobel_detekcja(obraz):
    """
    Wykonuje detekcję krawędzi algorytmem Sobela.
    Args:
        obraz (numpy.ndarray): Tablica z danymi obrazu (2D)
    Returns:
        tuple: (gradient_magnitude, gradient_x, gradient_y)
    """
    if obraz is None:
        print("Błąd: Brak danych wejściowych")
        return None, None, None

    # Normalizacja do zakresu 0-255
    obraz_norm = ((obraz - obraz.min()) / (obraz.max() - obraz.min()) * 255).astype(np.uint8)

    # Operatory Sobela
    sobel_x = ndimage.sobel(obraz_norm, axis=1)
    sobel_y = ndimage.sobel(obraz_norm, axis=0)

    # Magnitude gradientu
    gradient_mag = np.hypot(sobel_x, sobel_y)

    return gradient_mag, sobel_x, sobel_y
