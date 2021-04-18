from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _

from .TimestampedModel import TimestampedModel


class ScraperModel(TimestampedModel):

    name = models.CharField(
        verbose_name=_("Name of scraper"),
        max_length=64,
        unique=True,
        db_index=True,
    )

    @classmethod
    def get(cls, name: str, create: bool = False) -> Optional["ScraperModel"]:
        try:
            return ScraperModel.objects.get(name=name)
        except ScraperModel.DoesNotExist:
            if create:
                return ScraperModel.objects.create(name=name)

    def __str__(self):
        return self.name
