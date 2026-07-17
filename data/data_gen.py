import numpy as np
from config import WORLD_MAX, WORLD_MIN, GRID_COLS, GRID_ROWS, NUM_ZONES, BUOYS

K_FEATURES=7
SAMPLES_PER_ZONE=100
NUM_ANCHORS=3
NOISE_STD=3.0
NUM_ZONES=16

centroids = {
    1: [-51, -78, -76], # ON A1
    2: [-66, -82, -76], # NEAR A1 -> DIR A2
    3: [-78, -77, -80], # MIDDLE A1-A2
    4: [-85, -65, -78], # NEAR A2 -> DIR A1
    5: [-83, -31, -80], # ON A2
    6: [-90, -68, -90], # NEAR A2 -> DIR A3
    7: [-90, -80, -72], # MIDDLE A2-A3
    8: [-75, -80, -68], # NEAR A3 -> DIR A2
    9: [-71, -84, -32], # ON A3
    10: [-83, -79, -59], # NEAR A3 -> DIR A1
    11: [-81, -79, -80], # MIDDLE A3-A1
    12: [-62, -84, -78], # NEAR A1 -> DIR A3
    13: [-74, -78, -81], # DISTANT A1 -> DIR CENTER
    14: [-73, -68, -82], # DISTANT A2 -> DIR CENTER
    15: [-77, -80, -74], # DISTANT A3 -> DIR CENTER
    16: [-75, -74, -81], # CENTER
}

data_points=[]
for zone, centroid in centroids.items():
 for _ in range(SAMPLES_PER_ZONE):
        noisy_raw=np.random.normal(centroid, NOISE_STD)
        noisy_rssi=np.clip(noisy_raw, -110, -30).astype(int)
        data_points.append((noisy_rssi, zone))     
np.random.shuffle(data_points)

zone_coords = {}
 
def zone_id(col, row):
    return row * GRID_COLS + col + 1

def cell_centroid(col, row):
    cell_w = (WORLD_MAX - WORLD_MIN) / GRID_COLS
    cell_h = (WORLD_MAX - WORLD_MIN) / GRID_ROWS
    cx = WORLD_MIN + (col + 0.5) * cell_w
    cy = WORLD_MIN + (row + 0.5) * cell_h
    return cx, cy
 
for row in range(GRID_ROWS):
    for col in range(GRID_COLS):
        zid = zone_id(col, row)
        cx, cy = cell_centroid(col, row)
        zone_coords[zid] = (cx, cy)

import os
os.makedirs("./data", exist_ok=True)
with open("./data/training_set.h", "w") as f:
    f.write("#ifndef __TRAINING_SET_H__\n")
    f.write("#define __TRAINING_SET_H__\n")
    f.write("\n")
    f.write(f"#define K_VALUE {K_FEATURES}\n")
    f.write(f"#define NUM_ANCHORS {NUM_ANCHORS}\n")
    f.write(f"#define NUM_ZONES {NUM_ZONES}\n")
    f.write(f"#define SAMPLES_PER_ZONE {SAMPLES_PER_ZONE}\n")
    f.write("#define DATABASE_SIZE (NUM_ZONES*SAMPLES_PER_ZONE)\n")
    f.write("\n")
    f.write("typedef struct {\n")
    f.write("   int8_t rssi[NUM_ANCHORS];\n")
    f.write("   uint8_t zone_id;\n")
    f.write("} Fingerprint;\n")
    f.write("\n")
    f.write("typedef struct {\n")
    f.write("   float distance;\n")
    f.write("   uint8_t zone_id;\n")
    f.write("} Neighbor;\n")
    f.write("\n")
    f.write("static const Fingerprint training_set[DATABASE_SIZE]={\n")
    for pts, zone in data_points:
        f.write(f"    {{ {{{pts[0]}, {pts[1]}, {pts[2]}}}, {zone} }},\n")
    f.write("};\n\n")
    f.write("#endif /* KNN_DATA_H */\n")
    
print(f"Generated {NUM_ZONES} zones ({GRID_COLS}x{GRID_ROWS} grid), "
      f"{len(data_points)} total training samples.")
print("Wrote ./data/training_set.h")