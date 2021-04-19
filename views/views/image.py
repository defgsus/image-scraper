from django.views import View
from django.http import HttpResponse

from image_scraper.models import ImageModel


class ImageView(View):

    def get(self, request, filename):
        try:
            model = ImageModel.objects.get(filename=filename)
        except ImageModel.DoesNotExist:
            try:
                model = ImageModel.objects.get(thumb_filename=filename)
            except ImageModel.DoesNotExist:
                return HttpResponse(status=404)

        return HttpResponse(
            content=model.load_file(),
            headers={"Mime-Type": model.mime_type()},
        )
