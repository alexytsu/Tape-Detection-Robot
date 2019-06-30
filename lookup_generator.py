import pickle

import numpy as np
import pandas as pd

COLOUR_LOOKUP = np.ones((256,256), dtype=np.uint8)
COLOUR_LOOKUP = COLOUR_LOOKUP * 4

BLUE = 1
RED = 2
YELLOW = 3
OTHER = 4
GREEN = 5
PURPLE = 6

blue_regions = [
    ((106,70),(116,255)),
    ((105,50),(112,255))
]

yellow_regions = [
    ((20,150),(30,240)),
    ((22,50),(27,240))
]

for region in blue_regions:
    threshold_lower, threshold_higher = region
    hl, sl = threshold_lower
    hh, sh = threshold_higher
    COLOUR_LOOKUP[sl:sh,hl:hh] = 1

for region in yellow_regions:
    threshold_lower, threshold_higher = region
    hl, sl = threshold_lower
    hh, sh = threshold_higher
    COLOUR_LOOKUP[sl:sh,hl:hh] = 3

file = open("LOOKUP.pkl", "wb")
pickle.dump(COLOUR_LOOKUP, file)
print(np.where(COLOUR_LOOKUP == 1))
print("FINISHED")
