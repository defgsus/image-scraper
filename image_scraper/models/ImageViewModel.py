from django.db import models
from django.utils.translation import gettext_lazy as _


from .TimestampedModel import TimestampedModel


class ImageViewModel(TimestampedModel):

    image = models.ForeignKey(
        verbose_name=_("Viewed image"),
        to="ImageModel",
        on_delete=models.CASCADE,
        related_name="image_views",
    )

    user = models.CharField(
        verbose_name=_("Username"),
        max_length=32,
    )
