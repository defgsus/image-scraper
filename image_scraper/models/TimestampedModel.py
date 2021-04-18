from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampedModel(models.Model):

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        verbose_name=_("Create at"),
        auto_now=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Create at"),
        auto_now_add=True,
        db_index=True,
    )
