from django.views import View
from django.shortcuts import render

from image_scraper.models import ImageModel
from clip_features import search_images


class SearchImagesView(View):

    def get(self, request):
        text = request.GET.get("q")

        if not text:
            image_qset = ImageModel.objects.all().order_by("pk")
        else:
            image_qset = search_images(text)

        images_data = []
        for image in image_qset[:23]:
            images_data.append({
                "pk": image.pk,
                "caption": image.caption,
                "scraper": image.scraper.name,
                "filename": image.filename or image.thumb_filename,
                "extension": image.file_extension(),
                "url": image.url,
            })

        context = {
            "images": images_data,
            "param_q": text or "",
        }
        return render(request, "views/search.html", context)
