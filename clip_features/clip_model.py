import clip


_CLIP_INSTANCES = dict()


def get_clip_model(name: str = "ViT-B/32", device: str = "cpu"):
    key = f"{name}/{device}"
    if key not in _CLIP_INSTANCES:
        _CLIP_INSTANCES[key] = clip.load(name=name, device=device)

    return _CLIP_INSTANCES[key]

