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
        if not pk or rate is None or not user:
            return HttpResponse(status=500)

        try:
            image = ImageModel.objects.get(pk=pk)
        except ImageModel.DoesNotExist:
            return HttpResponse(status=404)

        kwargs = {
            "image": image,
            "user": user,
            "rate": rate,
        }
        if not ImageRateModel.objects.filter(**kwargs).exists():
            ImageRateModel.objects.create(**kwargs)

        return HttpResponse(status=201)


