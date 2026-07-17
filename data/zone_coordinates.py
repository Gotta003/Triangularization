# data/zone_coordinates.py
from config import Coordinates

# Coordinate fisiche stabili dei baricentri dei macro-settori
GENERATED_ZONE_COORDINATES = {
    # --- GRUPPO 1: SOPRA LE BOE (ON BOARDS) ---
    1: Coordinates(15.0, 15.0),   # ON A1 (Forte solo su A1: -51)
    5: Coordinates(55.0, 15.0),   # ON A2 (Forte solo su A2: -31)
    9: Coordinates(35.0, 55.0),   # ON A3 (Forte solo su A3: -32)[cite: 5]

    # --- GRUPPO 2: PUNTI MEDI SUI LATI (MIDDLE) ---
    3: Coordinates(35.0, 15.0),   # MIDDLE A1-A2 (Punto medio esatto sulla linea di fondo)[cite: 5]
    7: Coordinates(45.0, 35.0),   # MIDDLE A2-A3 (Punto medio esatto sulla linea destra)[cite: 5]
    11: Coordinates(25.0, 35.0),  # MIDDLE A3-A1 (Punto medio esatto sulla linea sinistra)[cite: 5]

    # --- GRUPPO 3: VICINO AD A1 (DIREZIONALI) ---
    2: Coordinates(22.0, 15.0),   # NEAR A1 -> DIR A2 (Spostato a destra verso A2)[cite: 5]
    12: Coordinates(18.0, 22.0),  # NEAR A1 -> DIR A3 (Spostato in alto verso A3)[cite: 5]
    13: Coordinates(23.0, 23.0),  # DISTANT A1 -> DIR CENTER (Diagonale verso il centro)[cite: 5]

    # --- GRUPPO 4: VICINO AD A2 (DIREZIONALI) ---
    4: Coordinates(48.0, 15.0),   # NEAR A2 -> DIR A1 (Spostato a sinistra verso A1)[cite: 5]
    6: Coordinates(52.0, 22.0),   # NEAR A2 -> DIR A3 (Spostato in alto verso A3)[cite: 5]
    14: Coordinates(47.0, 23.0),  # DISTANT A2 -> DIR CENTER (Diagonale verso il centro)[cite: 5]

    # --- GRUPPO 5: VICINO AD A3 (DIREZIONALI) ---
    8: Coordinates(39.0, 48.0),   # NEAR A3 -> DIR A2 (Spostato in basso a destra verso A2)[cite: 5]
    10: Coordinates(31.0, 48.0),  # NEAR A3 -> DIR A1 (Spostato in basso a sinistra verso A1)[cite: 5]
    15: Coordinates(35.0, 44.0),  # DISTANT A3 -> DIR CENTER (Sotto la boa A3, verso il centro)[cite: 5]

    # --- GRUPPO 6: IL CENTRO ---
    16: Coordinates(35.0, 31.0),  # CENTER (Equidistante da tutte le boe, baricentro del triangolo)[cite: 5]
}