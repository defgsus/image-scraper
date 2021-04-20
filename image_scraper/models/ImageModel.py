from django.db import models
from django.utils.translation import gettext_lazy as _

import PIL.Image

from .TimestampedModel import TimestampedModel
from scrapers import ScrapingSession


class ImageModel(TimestampedModel):

    scraper = models.ForeignKey(
        verbose_name=_("Scraper that retrieved the image"),
        to="ScraperModel",
        on_delete=models.CASCADE,
        db_index=True,
    )

    meta_data = models.ForeignKey(
        verbose_name=_("Link to meta-info"),
        to="MetaModel",
        on_delete=models.CASCADE,
    )

    filename = models.CharField(
        verbose_name=_("Filename of downloaded image"),
        max_length=128,
        db_index=True,
    )

    url = models.URLField(
        verbose_name=_("URL of image"),
        max_length=1024,
        null=True,
        db_index=True,
    )

    thumb_filename = models.CharField(
        verbose_name=_("Filename of downloaded thumbnail image"),
        max_length=128,
        db_index=True,
    )

    thumb_url = models.URLField(
        verbose_name=_("URL of thumbnail image"),
        max_length=1024,
        null=True,
        db_index=True,
    )

    caption = models.CharField(
        verbose_name=_("Caption of image"),
        max_length=1024,
        null=True,
        db_index=True,
    )

    def __str__(self):
        return f"{self.scraper.name}/{self.pk}"

    def load_image(self) -> PIL.Image.Image:
        filename = self.filename or self.thumb_filename
        filename = ScrapingSession.IMAGE_DIR / filename
        return PIL.Image.open(filename)

    def load_file(self) -> bytes:
        filename = self.filename or self.thumb_filename
        filename = ScrapingSession.IMAGE_DIR / filename
        with open(filename, "rb") as fp:
            return fp.read()

    def file_extension(self):
        fn = (self.filename or self.thumb_filename).lower()
        return fn.split(".")[-1]

    def mime_type(self) -> str:
        ext = self.file_extension()
        if ext == "jpeg":
            ext = "jpg"
        return f"imag/{ext}"

