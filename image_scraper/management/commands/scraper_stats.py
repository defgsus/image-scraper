import os
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from image_scraper.models import ScraperModel, ImageModel


class Command(BaseCommand):
    help = 'Display numbers'

    def add_arguments(self, parser):
        parser.add_argument(
            "--scraper", type=str, nargs="+",
            help="One or many scraper names to display"
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
            count = qset.count()
            print(f"{scraper}: {count} images")
