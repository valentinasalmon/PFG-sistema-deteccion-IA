"""Fechas de lanzamiento de dispositivos, para detectar capturas imposibles.

Una foto no puede haberse tomado con un modelo antes de que existiera
(RF39 CA2). La tabla es editable: un modelo que no figura no genera ninguna
anomalía. Se busca el nombre más largo que aparezca en el modelo declarado,
para que "iPhone 15 Pro" no se confunda con "iPhone 15".

Realiza: RF39 (CA2).
"""
from datetime import date

LANZAMIENTOS = {
    # Apple
    "iphone x": date(2017, 11, 3),
    "iphone xr": date(2018, 10, 26),
    "iphone xs": date(2018, 9, 21),
    "iphone 11": date(2019, 9, 20),
    "iphone 11 pro": date(2019, 9, 20),
    "iphone se (2nd generation)": date(2020, 4, 24),
    "iphone 12": date(2020, 10, 23),
    "iphone 12 pro": date(2020, 10, 23),
    "iphone 12 mini": date(2020, 11, 13),
    "iphone 13": date(2021, 9, 24),
    "iphone 13 pro": date(2021, 9, 24),
    "iphone 13 mini": date(2021, 9, 24),
    "iphone 14": date(2022, 9, 16),
    "iphone 14 pro": date(2022, 9, 16),
    "iphone 14 plus": date(2022, 10, 7),
    "iphone 15": date(2023, 9, 22),
    "iphone 15 pro": date(2023, 9, 22),
    "iphone 16": date(2024, 9, 20),
    "iphone 16 pro": date(2024, 9, 20),
    "iphone 16e": date(2025, 2, 28),
    "iphone 17": date(2025, 9, 19),
    # Samsung (código de modelo que figura en EXIF)
    "sm-g991": date(2021, 1, 29),  # Galaxy S21
    "sm-g996": date(2021, 1, 29),  # Galaxy S21+
    "sm-g998": date(2021, 1, 29),  # Galaxy S21 Ultra
    "sm-s901": date(2022, 2, 25),  # Galaxy S22
    "sm-s908": date(2022, 2, 25),  # Galaxy S22 Ultra
    "sm-s911": date(2023, 2, 17),  # Galaxy S23
    "sm-s918": date(2023, 2, 17),  # Galaxy S23 Ultra
    "sm-s921": date(2024, 1, 31),  # Galaxy S24
    "sm-s928": date(2024, 1, 31),  # Galaxy S24 Ultra
    "sm-s931": date(2025, 2, 7),  # Galaxy S25
    "sm-a546": date(2023, 3, 24),  # Galaxy A54
    "sm-a556": date(2024, 3, 11),  # Galaxy A55
    # Google
    "pixel 6": date(2021, 10, 28),
    "pixel 7": date(2022, 10, 13),
    "pixel 8": date(2023, 10, 12),
    "pixel 9": date(2024, 8, 22),
    # Motorola
    "moto g84": date(2023, 9, 1),
    "edge 40": date(2023, 5, 4),
}


def fecha_de_lanzamiento(modelo):
    """Fecha de lanzamiento del modelo declarado, o None si no se conoce."""
    texto = str(modelo or "").strip().lower()
    if not texto:
        return None
    coincidencias = [clave for clave in LANZAMIENTOS if clave in texto]
    if not coincidencias:
        return None
    return LANZAMIENTOS[max(coincidencias, key=len)]
