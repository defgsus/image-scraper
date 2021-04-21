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
            "param_q_amt": 1.,
            "param_qn": "",
            "param_qn_amt": 0.5,
            "param_count": 20,
            "param_sim": "",
            "param_sim_amt": .01,
        }
        return render(request, "views/search.html", context)

    def post(self, request):
        params = request.POST
        text_include = params.get("q") or "a beautiful sunset"
        text_exclude = params.get("qn") or ""
        similar_pk = params.get("sim") or ""
        try:
            count = int(params.get("count", 20))
        except:
            count = 20
        try:
            include_amount = float(params.get("q_amt") or 0.)
        except:
            include_amount = 0.
        try:
            exclude_amount = float(params.get("qn_amt") or 0.)
        except:
            exclude_amount = 0.
        try:
            similar_amount = float(params.get("sim_amt") or 0.)
        except:
            similar_amount = 0.

        # get all image features (as much as fits in memory)
        pks, image_features = cached_image_features()

        # convert text to features

        text_features = [text_include, text_exclude]
        search_features = get_text_features(text_features)

        # add image similarity features
        if similar_pk:
            try:
                sim_image = ImageModel.objects.get(pk=similar_pk)
                assert sim_image.image_features.ok
                search_features = np.append(
                    search_features,
                    [sim_image.image_features.features],
                    axis=0,
                )
            except (ImageModel.DoesNotExist, AssertionError):
                similar_pk = ""

        # calculate scores for each image
        scores = 100. * search_features @ image_features.T

        # combine scores
        if text_include:
            combined_scores = include_amount * scores[0]
        else:
            combined_scores = 0. * scores[0]

        if text_exclude and exclude_amount:
             combined_scores -= exclude_amount * scores[1]

        if len(scores) > 2:
            combined_scores += similar_amount * scores[2]

        # get indices of top <count> images and load image info from database
        top_idxs = np.argsort(combined_scores)[::-1][:count].tolist()

        top_images = [
            (ImageModel.objects.get(pk=pks[i]), combined_scores[i])
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
            "param_q_amt": include_amount,
            "param_qn": text_exclude,
            "param_qn_amt": exclude_amount,
            "param_sim": similar_pk,
            "param_sim_amt": similar_amount,
            "param_count": count,
        }
        response = render(request, "views/search.html", context)
        response.headers["Content-Security-Policy"] = "script-src 'self' 'unsafe-inline' 'unsafe-eval'"
        return response
