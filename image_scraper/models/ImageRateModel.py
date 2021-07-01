from django.db import models
from django.utils.translation import gettext_lazy as _


from .TimestampedModel import TimestampedModel


class ImageRateModel(TimestampedModel):

    image = models.ForeignKey(
        verbose_name=_("Rated image"),
        to="ImageModel",
        on_delete=models.CASCADE,
    )

    user = models.CharField(
        verbose_name=_("Rating username"),
        max_length=32,
    )

    rate = models.SmallIntegerField(
        verbose_name=_("Integer rating value"),
    )
