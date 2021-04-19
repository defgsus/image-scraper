from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

from image_scraper.models.TimestampedModel import TimestampedModel


class ClipFeatures(TimestampedModel):
    """
    This records the CLIP image features for an ImageModel.

    Either the thumb or the original image is used if present
    """

    image = models.OneToOneField(
        verbose_name=_("The associated image"),
        to="image_scraper.ImageModel",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="image_features",
    )

    ok = models.BooleanField(
        verbose_name=_("Feature processing worked"),
    )

    features = ArrayField(
        verbose_name=_("CLIP image features"),
        base_field=models.FloatField(),
        null=True,
    )

    def __str__(self):
        return f"{self.image}"
