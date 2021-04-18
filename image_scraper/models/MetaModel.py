from django.db import models
from django.utils.translation import gettext_lazy as _

from .TimestampedModel import TimestampedModel


class MetaModel(TimestampedModel):

    scraper = models.ForeignKey(
        verbose_name=_("Scraper that retrieved the image that is meta-infoed"),
        to="ScraperModel",
        on_delete=models.CASCADE,
        db_index=True,
    )

    type = models.CharField(
        verbose_name=_("Type of info"),
        max_length=32,
        db_index=True,
    )

    meta_id = models.CharField(
        verbose_name=_("Some freely chooseable ID"),
        max_length=64,
        db_index=True,
        null=True,
    )

    data = models.JSONField(
        verbose_name=_("Any meta information"),
        null=True,
    )

    def __str__(self):
        return f"{self.type}/{self.meta_id}"
