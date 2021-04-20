from django.views import View
from django.http import HttpResponse

from image_scraper.models import ImageModel


class ImageView(View):

    def get(self, request, filename):
        try:
            pk, ext = filename.split(".")
        except:
            return HttpResponse(status=404)

        try:
            model = ImageModel.objects.get(pk=pk)
        except ImageModel.DoesNotExist:
            return HttpResponse(status=404)

        try:
            return HttpResponse(
                content=model.load_file(),
                headers={"Mime-Type": model.mime_type()},
            )
        except:
            return HttpResponse(status=500)
