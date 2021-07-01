import os
import glob
import json
from typing import Generator, Tuple, List

from django.conf import settings

import numpy as np

CACHE_DIR = settings.BASE_DIR / "cache" / "features"


_cached_features = dict()


def cached_image_features(scraper_name: str) -> Tuple[List[int], np.ndarray]:
    global _cached_features
    if scraper_name not in _cached_features:
        _cached_features[scraper_name] = {
            "features": np.load(CACHE_DIR / scraper_name / "features_0.npy")
        }

        _cached_features[scraper_name]["features"] /= np.linalg.norm(
            _cached_features[scraper_name]["features"],
            axis=-1, keepdims=True
        )

        with open(CACHE_DIR / scraper_name / f"pks_0.json") as fp:
            _cached_features[scraper_name]["pks"] = json.load(fp)

    return _cached_features[scraper_name]["pks"], _cached_features[scraper_name]["features"]


def iter_cached_features() -> Generator[Tuple[List[int], np.ndarray], None, None]:
    """
    Iterates through all cached features

    :return: generator of tuple of
        (list of PKS, numpy.ndarray)
    """
    feature_files = sorted(glob.glob(str(CACHE_DIR / "*" / "features_*.npy")))

    for feature_fn in feature_files:
        features = np.load(feature_fn)

        idx = feature_fn.split("_")[-1][:-4]
        with open(CACHE_DIR / f"pks_{idx}.json") as fp:
            pks = json.load(fp)

        yield pks, features
