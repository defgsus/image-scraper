import os
import json
from typing import List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import numpy as np
from tqdm import tqdm

from image_scraper.models import ScraperModel, ImageModel
from clip_features.models import ClipFeatures
from clip_features.cache import CACHE_DIR


class Command(BaseCommand):
    help = 'Render out features and index of images'

    def add_arguments(self, parser):
        parser.add_argument(
            "scraper", type=str,
            help="Name of scraper"
        )
        parser.add_argument(
            "--batch-size", type=int, default=1024,
            help="Number of images/features to export in one file"
        )

    def handle(self, *args, **options):
        export_features(**options)


def export_features(
        scraper: str,
        batch_size: int,
        verbosity: int = 0,
        **kwargs,
):
    scraper_model = None
    try:
        scraper_model = ScraperModel.objects.get(name=scraper)
    except ScraperModel.DoesNotExist:
        print(f"Unknown scraper '{scraper}'")
        exit(1)

    full_qset = (
        ImageModel.objects
            .filter(scraper=scraper_model)
            .exclude(image_features=None)
            .exclude(image_features__ok=False)
            .order_by("pk")
    )

    count = full_qset.count()
    if not batch_size:
        batch_size = count

    with tqdm(total=count) as progress:
        for batch_num in range(0, count // batch_size + 1):

            batch_qset = full_qset[batch_num * batch_size: (batch_num + 1) * batch_size]
            features = list(batch_qset.values_list("image_features__features", flat=True))
            if not features:
                break

            features = np.stack(features).astype(np.float16)

            np.save(f"export_{scraper}_{batch_num:04}_features.npy", features)
            del features

            multi_meta_data = list(batch_qset.values(
                "pk",
                "filename", "url", "thumb_filename", "thumb_url",
                "caption",
                "meta_data__type",
                "meta_data__id",
                "meta_data__data",
                "imageratemodel__user",
                "imageratemodel__rate",
            ))
            meta_data = {}
            for data in multi_meta_data:
                rating = {
                    "user": data.pop("imageratemodel__user"),
                    "rate": data.pop("imageratemodel__rate")
                }
                meta = {
                    "type": data.pop("meta_data__type"),
                    "id": data.pop("meta_data__id"),
                    "data": data.pop("meta_data__data"),
                }
                if data["pk"] not in meta_data:
                    data.update({
                        "rating": [rating],
                        "meta": [meta]
                    })
                    meta_data[data["pk"]] = data
                else:
                    if rating not in meta_data[data["pk"]]["rating"]:
                        meta_data[data["pk"]]["rating"].append(rating)
                    if meta not in meta_data[data["pk"]]["meta"]:
                        meta_data[data["pk"]]["meta"].append(meta)

            meta_data = [meta_data[key] for key in sorted(meta_data)]

            # print(json.dumps(meta_data, indent=2))
            with open(f"export_{scraper}_{batch_num:04}_meta.json", "w") as fp:
                json.dump(meta_data, fp)

            progress.update(len(meta_data))
