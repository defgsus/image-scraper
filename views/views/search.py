from django.views import View
from django.shortcuts import render

from image_scraper.models import ImageModel
from clip_features import search_images


class SearchImagesView(View):

    def get(self, request):
        text = request.GET.get("q")
        try:
            count = int(request.GET.get("count", 20))
        except:
            count = 20

        if not text:
            images = [
                (img, 0)
                for img in ImageModel.objects.all().order_by("pk")[:count]
            ]
        else:
            images = search_images(text, count=count)

        images_data = []
        for image, score in images:
            images_data.append({
                "pk": image.pk,
                "caption": image.caption,
                "scraper": image.scraper.name,
                "filename": image.filename or image.thumb_filename,
                "extension": image.file_extension(),
                "url": image.url,
                "score": round(score, 2),
            })

        context = {
            "images": images_data,
            "param_q": text or "",
            "param_count": count,
        }
        return render(request, "views/search.html", context)
