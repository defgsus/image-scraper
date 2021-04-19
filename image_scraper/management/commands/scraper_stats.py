import os
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from image_scraper.models import ScraperModel, ImageModel, MetaModel


class Command(BaseCommand):
    help = 'Display numbers'

    def add_arguments(self, parser):
        parser.add_argument(
            "--scraper", type=str, nargs="+",
            help="One or many scraper names to display, leave empty to show all"
        )

    def handle(self, *args, **options):
        if not options["scraper"]:
            scrapers = list(ScraperModel.objects.all().values_list("name", flat=True).distinct())
        else:
            scrapers = options["scraper"]

        for scraper in scrapers:
            scraper_model = ScraperModel.get(scraper)
            if not scraper_model:
                print(f"{scraper}: unknown")
                continue

            qset = ImageModel.objects.filter(scraper=scraper_model)
            meta_qset = MetaModel.objects.filter(scraper=scraper_model)
            feature_qset = qset.exclude(image_features=None)
            print(f"{scraper}:")
            print(f"  {meta_qset.count():10} meta infos")
            print(f"  {qset.count():10} images")
            print(f"  {feature_qset.filter(image_features__ok=True).count():10} image features")
            num_failures = feature_qset.filter(image_features__ok=False).count()
            if num_failures:
                print(f"  {num_failures:10} image features failed")
