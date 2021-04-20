from typing import List, Tuple

import numpy as np

from .clip_model import get_text_features


def search_images(text: str, count: int = 20) -> List[Tuple["ImageModel", float]]:
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
