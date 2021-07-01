from typing import List, Tuple

import numpy as np

from .clip_model import get_text_features
from .cache import CACHE_DIR, iter_cached_features, cached_image_features


def search_images(scraper_name: str, text: str, count: int = 20) -> List[Tuple["ImageModel", float]]:
    from image_scraper.models import ImageModel

    text_features = get_text_features(text)

    pks, image_features = cached_image_features(scraper_name=scraper_name)

    sim = text_features @ image_features.T

    top_idxs = np.argsort(sim)[::-1][:count].tolist()

    return [
        (ImageModel.objects.get(pk=pks[i]), sim[i])
        for i in top_idxs
    ]


def search_images_batch_iter(text: str, count: int = 20) -> List[Tuple["ImageModel", float]]:
    from image_scraper.models import ImageModel

    text_features = get_text_features(text)

    top_pks = []
    for pks, image_features in iter_cached_features():

        sim = 100. * text_features @ image_features.T

        #top_idxs = np.argsort(sim)[::-1]
        top_pks += [(s, pks[i]) for i, s in enumerate(sim)]

    top_pks.sort(key = lambda i: -i[0])

    return [
        (ImageModel.objects.get(pk=pk), s)
        for s, pk in top_pks[:count]
    ]


def search_images_db(text: str, count: int = 20) -> List[Tuple["ImageModel", float]]:
    """
    Unperformant search in DB features
    Not feasible for many images
    """
    from image_scraper.models import ImageModel

    text_features = get_text_features(text)

    images = ImageModel.objects.all()

    image_features = images.values_list("image_features__features", flat=True)

    image_features = np.stack(image_features)

    sim = 100. * text_features @ image_features.T

    top_idxs = np.argsort(sim)[::-1][:count].tolist()

    return [
        images[i] for i in top_idxs
    ]
