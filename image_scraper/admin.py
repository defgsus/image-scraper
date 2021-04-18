from django.contrib import admin
from django.contrib.admin.decorators import register

from .models import ImageModel, MetaModel, ScraperModel


@register(ScraperModel)
class ScraperModelAdmin(admin.ModelAdmin):

    list_display = ("pk", "name", )


@register(ImageModel)
class ImageModelAdmin(admin.ModelAdmin):

    list_display = ("pk", "scraper", "meta_data", "url", "thumb_url", "caption")


@register(MetaModel)
class MetaModelAdmin(admin.ModelAdmin):

    list_display = ("pk", "scraper", "type", "meta_id", "data")
