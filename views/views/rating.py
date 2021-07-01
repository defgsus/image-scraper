import json

from django.views import View
from django.http import HttpResponse

from image_scraper.models import ImageModel, ImageRateModel


class ImageRatingView(View):

    def post(self, request):
        params = json.loads(request.body.decode("utf-8"))
        pk = params.get("pk")
        rate = params.get("rate")
        user = params.get("user")
        remove = bool(params.get("remove"))

        if pk is None or rate is None or user is None:
            return HttpResponse(status=500)

        try:
            image = ImageModel.objects.get(pk=pk)
        except ImageModel.DoesNotExist:
            return HttpResponse(status=404)

        kwargs = {
            "image": image,
            "user": user,
        }
        rating_exists = ImageRateModel.objects.filter(**kwargs).exists()
        if remove:
            if not rating_exists:
                return HttpResponse(status=404)
            else:
                ImageRateModel.objects.filter(**kwargs).delete()
                return HttpResponse(status=201)
        else:
            if rating_exists:
                ImageRateModel.objects.filter(**kwargs).delete()

            ImageRateModel.objects.create(**kwargs, rate=rate)
            return HttpResponse(status=201)


