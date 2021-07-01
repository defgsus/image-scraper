import os
import sys
import urllib.request
import zipfile
import csv
from io import StringIO

from tqdm import tqdm

from image_scraper.models import ScraperModel, MetaModel, ImageModel
from scrapers import ScrapingSession


def main(args: dict):
    def log(*a):
        if args["verbosity"] > 1:
            print(*a, file=sys.stderr)

    zip_filename = ScrapingSession.CACHE_DIR / "unsplash" / "lite.zip"
    zip_url = "https://unsplash.com/data/lite/latest"

    if not os.path.exists(zip_filename):
        os.makedirs(zip_filename.parent, exist_ok=True)
        log(f"downloading {zip_url} to {zip_filename}")
        _download_tables(zip_url, zip_filename)

    _download_images(zip_filename)


def _download_tables(url: str, filename: str):
    with urllib.request.urlopen(url) as source, open(filename, "wb") as output:
        with tqdm(total=int(source.info().get("Content-Length")), ncols=80, unit='iB', unit_scale=True) as loop:
            while True:
                buffer = source.read(8192)
                if not buffer:
                    break

                output.write(buffer)
                loop.update(len(buffer))


def _download_images(filename: str):
    with zipfile.ZipFile(filename) as zipf:
        with zipf.open("photos.tsv000", "r") as fp:
            image_table = fp.read().decode("utf-8")

    fp = StringIO(image_table)

    rows = list(csv.DictReader(fp, delimiter="\t"))

    session = ScrapingSession("unsplash", {"cached": True})
    scraper_model = ScraperModel.get("unsplash", create=True)

    try:
        meta_model = MetaModel.objects.get(
            scraper=scraper_model,
            type="little-dataset",
        )
    except MetaModel.DoesNotExist:
        meta_model = MetaModel.objects.create(
            scraper=scraper_model,
            type="little-dataset",
        )

    for row in tqdm(rows):
        photo_url = row["photo_image_url"]
        page_url = row["photo_url"]

        filename, downloaded = session.download_image(
            url=photo_url,
            short_filename=True,
        )
        if not ImageModel.objects.filter(filename=filename).exists():
            ImageModel.objects.create(
                scraper=scraper_model,
                meta_data=meta_model,
                filename=filename,
                # Note! This is a url to a html-page, not the actual image
                url=page_url,
            )
