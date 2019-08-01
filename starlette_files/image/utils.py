try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


def has_alpha(image: Image) -> bool:
    return image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    )


def to_rgb(image: Image) -> Image:
    # convert 1 and P images to RGB to improve resize quality
    if image.mode in ["1", "P"]:
        if has_alpha(image):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")
    return image
