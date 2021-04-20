import os
import glob
import json
from typing import Generator, Tuple, List

from django.conf import settings

import numpy as np

CACHE_DIR = settings.BASE_DIR / "cache" / "features"


def iter_cached_features() -> Generator[Tuple[List[int], np.ndarray], None, None]:
    """
    Iterates through all cached features
    :return: generator of tuple of
        (list of PKS, numpy.ndarray)
    """
    feature_files = sorted(glob.glob(str(CACHE_DIR / "features_*.npy")))

    for feature_fn in feature_files:
        features = np.load(feature_fn)

        idx = feature_fn.split("_")[-1][:-4]
        with open(CACHE_DIR / f"pks_{idx}.json") as fp:
            pks = json.load(fp)

        yield pks, features
