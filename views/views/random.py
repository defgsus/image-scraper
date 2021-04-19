from django.views import View
from django.shortcuts import render

from image_scraper.models import ImageModel


class RandomImagesView(View):

    def get(self, request):
        image_qset = ImageModel.objects.all().order_by("pk")

        images_data = []
        for image in image_qset[:10]:
            images_data.append({
                "caption": image.caption,
                "scraper": image.scraper.name,
                "filename": image.filename or image.thumb_filename,
            })

        context = {
            "images": images_data
        }
        print(context)
        return render(request, "views/random.html", context)
