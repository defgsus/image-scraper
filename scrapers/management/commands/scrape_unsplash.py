import os
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from scrapers.scrapers import unsplash


class Command(BaseCommand):
    help = 'Download unsplash dataset'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        unsplash.main(options)
