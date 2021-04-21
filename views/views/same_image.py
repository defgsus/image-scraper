from django.views import View
from django.shortcuts import render
from django.http import HttpResponse

import numpy as np

from image_scraper.models import ImageModel
from clip_features.clip_model import get_text_features
from clip_features.cache import cached_image_features


class SameImagesView(View):

    def get(self, request, pk):
        try:
            count = int(request.GET.get("count", 20))
        except:
            count = 20

        try:
            image = ImageModel.objects.get(pk=pk)
            image_features = image.image_features.features
            assert len(image_features)
        except:
            return HttpResponse(status=404)

        image_features = np.asarray(image_features)

        pks, all_image_features = cached_image_features()

        scores = image_features @ all_image_features.T

        top_idxs = np.argsort(scores)[::-1][:count].tolist()

        top_images = [
            (ImageModel.objects.get(pk=pks[i]), scores[i])
            for i in top_idxs
        ]

        images_data = []
        for image, score in top_images:
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
            "param_count": count,
        }
        return render(request, "views/same.html", context)
