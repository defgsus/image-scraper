from django.views import View
from django.shortcuts import render

import numpy as np

from image_scraper.models import ImageModel
from clip_features.clip_model import get_text_features
from clip_features.cache import cached_image_features


class SearchImagesView(View):

    def get(self, request):
        context = {
            "param_q": "a beautiful sunset",
            "param_qn": "",
            "param_qn_amt": "0.5",
            "param_count": 20,
        }
        return render(request, "views/search.html", context)

    def post(self, request):
        params = request.POST
        text_include = params.get("q") or "a beautiful sunset"
        text_exclude = params.get("qn") or ""
        try:
            count = int(params.get("count", 20))
        except:
            count = 20
        try:
            exclude_amount = float(params.get("qn_amt") or 0.)
        except:
            exclude_amount = 0.

        pks, image_features = cached_image_features()

        text_features = np.stack([
            get_text_features(text_include),
            get_text_features(text_exclude),
        ])

        scores = text_features @ image_features.T

        if text_exclude and exclude_amount:
            scores = scores[0] - exclude_amount * scores[1]
        else:
            scores = scores[0]

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
            "param_q": text_include,
            "param_qn": text_exclude,
            "param_qn_amt": exclude_amount,
            "param_count": count,
        }
        return render(request, "views/search.html", context)
