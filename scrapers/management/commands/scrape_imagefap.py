import os
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from scrapers.scrapers import imagefap


class Command(BaseCommand):
    help = 'Download imagefap images'

    def add_arguments(self, parser):
        parser.add_argument(
            "--gallery", type=str, nargs="+",
            help="One or many URLs or numbers of imagefap galleries"
        )
        parser.add_argument(
            "--search", type=str,
            help="A search keyword to scrape for galleries",
        )
        parser.add_argument(
            "--pages", type=int, default=1,
            help="Number of search pages to scrape, default = 1",
        )
        parser.add_argument(
            "-c", "--cached", type=bool, nargs="?", default=False, const=True,
            help="Cache website requests (for development)"
        )

    def handle(self, *args, **options):
        imagefap.main(options)
