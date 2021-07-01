import json
import math

from django.views import View
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.urls import reverse

import numpy as np

from image_scraper.models import ImageModel, ScraperModel, ImageRateModel
from clip_features.clip_model import get_text_features
from clip_features.cache import cached_image_features


class SearchImagesView(View):

    def get(self, request):
        context = {
            "extra_css": ["views/search.css"],
            "extra_js": ["views/search.js"],
            "scrapers": list(
                ScraperModel.objects.all().order_by("name").values_list("name", flat=True)
            )
        }
        return render(request, "views/search.html", context)

    def post(self, request):
        params = json.loads(request.body.decode("utf-8"))
        params.setdefault("count", 20)

        # get all image features (as much as fits in memory)
        pks, image_features = cached_image_features(scraper_name=params["scraper"])

        # convert search requests to features

        search_features = []
        feature_amounts = []
        for row in params["search_rows"]:
            if row["amount"] == 0:
                continue

            if row["type"] == "text":
                search_features.append(get_text_features(row["value"]))
                feature_amounts.append(row["amount"] / 5.)

            elif row["type"] == "image":
                try:
                    sim_image = ImageModel.objects.get(pk=row["value"])
                    assert sim_image.image_features.ok
                    features = sim_image.image_features.features
                    search_features.append(features)
                    amt = row["amount"] / 5. / 3.
                    #amt = amt * amt * math.copysign(1, amt) / 5.
                    feature_amounts.append(amt)
                except (ImageModel.DoesNotExist, AssertionError):
                    pass

        images_data = []

        if search_features:
            search_features = np.asarray(search_features)
            search_features /= np.linalg.norm(search_features, axis=-1, keepdims=True)
            feature_amounts = np.asarray(feature_amounts)

            # calculate scores for each image
            scores = 100. * search_features @ image_features.T

            # apply feature matching weights
            scores *= feature_amounts[:, None]

            combined_scores = np.sum(scores, axis=0)

            # get indices of top <count> images and load image info from database
            top_idxs = np.argsort(combined_scores)[::-1][:params["count"]].tolist()

            top_images = [
                (ImageModel.objects.get(pk=pks[i]), combined_scores[i])
                for i in top_idxs
            ]

            for image, score in top_images:
                images_data.append({
                    "pk": image.pk,
                    "caption": image.caption,
                    "scraper": image.scraper.name,
                    "url": reverse(
                        "views:image",
                        args=[image.filename or image.thumb_filename],
                    ),
                    "original_url": image.url,
                    "score": round(score, 2),
                })

        # -- attach image ratings for current user --

        image_ratings = ImageRateModel.objects.filter(
            user=params.get("user") or "",
            image__pk__in=[i["pk"] for i in images_data]
        ).values_list("image__pk", "rate")
        image_ratings = {r[0]: r[1] for r in image_ratings}
        for i in images_data:
            i["rating"] = image_ratings.get(i["pk"], 0)

        return JsonResponse({
            "images": images_data,
        })
