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
        parser.add_argument(
            "scraper", type=str,
            help="Name of scraper"
        )
        parser.add_argument(
            "--batch-size", type=int, default=0,
            help="Number of image features to pack into one numpy file. default is all images"
        )

    def handle(self, *args, **options):
        store_feature_cache(**options)


def store_feature_cache(
        scraper: str,
        batch_size: int = 0,
        verbosity: int = 0,
        **kwargs,
):
    scraper_model = None
    try:
        scraper_model = ScraperModel.objects.get(name=scraper)
    except ScraperModel.DoesNotExist:
        print(f"Unknown scraper '{scraper}'")
        exit(1)

    qset = (
        ImageModel.objects
            .filter(scraper=scraper_model)
            .exclude(image_features=None)
            .exclude(image_features__ok=False)
            .order_by("pk")
    )

    count = qset.count()
    if not batch_size:
        batch_size = count

    for i in range(0, count, batch_size):
        if verbosity > 1:
            print(f"exporting {batch_size} / {count} features")

        batch_qset = qset[i*batch_size:(i+1)*batch_size]
        features = batch_qset.values_list("image_features__features", flat=True)

        features = np.stack(features)

        os.makedirs(CACHE_DIR / scraper, exist_ok=True)
        np.save(CACHE_DIR / scraper / f"features_{i}.npy", features)
        del features

        pks = list(batch_qset.values_list("pk", flat=True))
        with open(CACHE_DIR / scraper / f"pks_{i}.json", "w") as fp:
            json.dump(pks, fp)
