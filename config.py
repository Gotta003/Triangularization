from dataclasses import dataclass
@dataclass(frozen=True)
class Coordinates:
    x: float
    y: float
    
from datetime import datetime
@dataclass(frozen=False)
class TelemetrySample:
    coordinates: Coordinates
    rssi: list[int]
    zone: int
    timestamp: datetime

SERIAL_PORT="/dev/cu.usbmodem1203"
BAUD_RATE=115200

WORLD_MIN=0.0
WORLD_MAX=70.0
GRID_COLS=5
GRID_ROWS=4
NUM_ZONES=16

def grid_cell_center(row: int, col: int) -> Coordinates:
    cell_w=(WORLD_MAX-WORLD_MIN)/GRID_COLS
    cell_h=(WORLD_MAX-WORLD_MIN)/GRID_ROWS
    x=WORLD_MIN+cell_w*(col+0.5)
    y=WORLD_MIN+cell_h*(row+0.5)
    return Coordinates(x,y)

def grid_zone_id(row: int, col: int) -> int:
    return row*GRID_COLS+col+1

from data.zone_coordinates import GENERATED_ZONE_COORDINATES
ZONE_COORDINATES=GENERATED_ZONE_COORDINATES

BUOYS = {
    "A1": (15.0, 15.0),
    "A2": (55.0, 15.0),
    "A3": (35.0, 55.0),
}