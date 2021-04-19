import os
import datetime
from typing import List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import torch

from image_scraper.models import ScraperModel, ImageModel
from clip_features import get_clip_model
from clip_features.models import ClipFeatures


class Command(BaseCommand):
    help = 'Calculate the CLIP image features for all images that do not have them yet'

    def add_arguments(self, parser):
        parser.add_argument(
            "--scraper", type=str, nargs="+",
            help="One or many scraper names to restrict the images to calculate"
        )
        parser.add_argument(
            "--batch-size", type=int, default=50,
            help="Number of images to process in one batch"
        )

    def handle(self, *args, **options):
        get_clip_features(**options)


def get_clip_features(
        scraper: Optional[List[str]] = None,
        batch_size: int = 50,
        verbosity: int = 0,
        **kwargs,
):
    if not scraper:
        scrapers = list(ScraperModel.objects.all().values_list("name", flat=True).distinct())
    else:
        scrapers = scraper

    for scraper in scrapers:
        scraper_model = ScraperModel.get(scraper)
        if not scraper_model:
            print(f"{scraper}: unknown")
            continue

        qset = ImageModel.objects.filter(
            scraper=scraper_model,
            image_features=None,
        ).order_by("pk")

        count_all = qset.count()
        if verbosity > 1:
            print(f"{scraper}: {count_all} images")

        num_processed_all = 0
        num_failed_all = 0
        while qset.exists():
            batch_qset = qset[:batch_size]

            num_processed, num_failed = _process_image_batch(list(batch_qset), verbosity=verbosity)

            num_processed_all += num_processed
            num_failed_all += num_failed

            if verbosity > 1:
                print(f"{scraper}: {num_processed_all}/{count_all} processed, {num_failed_all} failed")


def _process_image_batch(images: List[ImageModel], device: str = "cpu", verbosity: int = 0):

    model, preprocess = get_clip_model(device=device)

    processed_image_models = []
    failed_image_models = []
    torch_image_batch = []
    for image_model in images:
        try:
            image = image_model.load_image()
            image = preprocess(image)
            torch_image_batch.append(image)
            processed_image_models.append(image_model)
        except:
            failed_image_models.append(image_model)

    with transaction.atomic():

        if torch_image_batch:
            torch_image_batch = torch.stack(torch_image_batch).to(device)

            with torch.no_grad():
                feature_batch = model.encode_image(torch_image_batch).cpu().numpy()

            for image_model, features in zip(processed_image_models, feature_batch):
                ClipFeatures.objects.create(
                    image=image_model,
                    ok=True,
                    features=features.tolist(),
                )

        for image_model in failed_image_models:
            ClipFeatures.objects.create(
                image=image_model,
                ok=False,
            )

    return len(processed_image_models), len(failed_image_models)
