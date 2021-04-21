from django.views import View
from django.http import HttpResponse

import PIL.Image

from image_scraper.models import ImageModel
from scrapers import ScrapingSession


class ImageView(View):

    def get(self, request, filename):
        if ".." not in filename:
            try:
                mime_type = filename.split(".")[-1]
                if mime_type == "jpeg":
                    mime_type = "jpg"
                mime_type = f"image/{mime_type}"

                full_name = ScrapingSession.IMAGE_DIR / filename
                with open(full_name, "rb") as fp:
                    return HttpResponse(
                        content=fp.read(),
                        headers={"Mime-Type": mime_type},
                    )
            except:
                pass

        return HttpResponse(status=404)
