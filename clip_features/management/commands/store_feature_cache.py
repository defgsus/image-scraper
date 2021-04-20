import os
import json
from typing import List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import numpy as np

from image_scraper.models import ScraperModel, ImageModel
from clip_features.models import ClipFeatures
from clip_features.cache import CACHE_DIR


class Command(BaseCommand):
    help = 'Create cache files of previously calculated image features'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        create_feature_cache(**options)


def create_feature_cache(
        batch_size: int = 100000,
        verbosity: int = 0,
        **kwargs,
):
    qset = ImageModel.objects.exclude(image_features=None).order_by("pk")

    count = qset.count()

    for i in range(0, count, batch_size):
        if verbosity > 1:
            print(f"exporting {batch_size} / {count} features")

        batch_qset = qset[i*batch_size:(i+1)*batch_size]
        features = batch_qset.values_list("image_features__features", flat=True)

        features = np.stack(features)

        os.makedirs(CACHE_DIR, exist_ok=True)
        np.save(CACHE_DIR / f"features_{i}.npy", features)
        del features

        pks = list(batch_qset.values_list("pk", flat=True))
        with open(CACHE_DIR / f"pks_{i}.json", "w") as fp:
            json.dump(pks, fp)
