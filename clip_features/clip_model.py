from typing import Union, List

import numpy as np
import torch

import clip


_CLIP_INSTANCES = dict()


def get_clip_model(name: str = "ViT-B/32", device: str = "cpu"):
    key = f"{device}/{name}"
    if key not in _CLIP_INSTANCES:
        _CLIP_INSTANCES[key] = clip.load(name=name, device=device)

    return _CLIP_INSTANCES[key]


def get_text_features(text: Union[str, List[str]], device: str = "cpu") -> np.ndarray:
    model, _ = get_clip_model()

    is_array = not isinstance(text, str)
    if not is_array:
        text = [text]

    tokens = clip.tokenize(text).to(device)
    with torch.no_grad():
        features = model.encode_text(tokens).cpu().numpy()

    features /= np.linalg.norm(features, axis=-1, keepdims=True)

    if is_array:
        return features
    else:
        return features[0]

