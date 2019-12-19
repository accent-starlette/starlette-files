# Image Operations

!!! warning "Before you continue"

    This section assumes you have worked through [handling images](../handling_images)
    and that you have your image model setup using an `ImageAttachment` class.

## About Operations

Lets say you have a bunch of images of random sizes and image formats such as `JPEG`
and `PNG`, but you want a consistent file output of say 100x100 and all `PNG`. Thats
is the purpose of these operations.
They take an image, use [pillow](https://pypi.org/project/Pillow/) to transform the image
based on filters you specify and save a new version of the file.

## Getting Started

You have your `ImageAttachment` class and `Image` table like below:

```python
import sqlalchemy as sa
from starlette_files.constants import MB
from starlette_files.fields import ImageAttachment

class ImageType(ImageAttachment):
    # your storage 
    storage = my_storage
    # directory in the stroage to save files to
    directory = "images"
    # allowed content types
    allowed_content_types = ["image/jpeg", "image/png"]
    # maximum allowed size in bytes
    max_length = MB * 5

class Image(Base):
    image = sa.Column(ImageType.as_mutable(sa.JSON))
```

Next create another SQLAlchemy field that uses `ImageRenditionAttachment`. This class uses
an instance of an `ImageAttachment` and has functionality to apply operations
on the file before being saved to the storage.

```python
from starlette_files.fields import ImageRenditionAttachment

class ImageRenditionType(ImageRenditionAttachment):
    storage = my_storage
    directory = "renditions"
```

and create another table to store the images:

```python
class ImageRendition(Base):
    image = sa.Column(ImageRenditionType.as_mutable(sa.JSON))
    original_image_id = sa.Column(sa.Integer, sa.ForeignKey("image.id"), nullable=False)
    original_image = sa.orm.relationship("Image", backref="renditions")
```

## Creating a Rendition

Once you have an instance of your `Image`:

```python
original_image = session.query(Image).first()
```

you can create a new rendition of it using a filter:

```python
rendition_obj = ImageRenditionType.create_from(
    attachment=original_image.image,
    filter_specs=["width-100"]
)
```

This will take the original image and make it 100px wide.
You can then save it as normal:

```python
session = Session()
instance = ImageRendition(image=rendition_obj, original_image=original_image)
session.add(instance)
session.commit()
```

## Filters

Below are the pre-existing filter operations.

### Crop

This allows you to take an image and crop it to a certain size. 

The format required for this is:

```python
f"crop-{left}x{top}x{width}x{height}"
```

For example an image of 200x200 that you want to crop to 100x100 in the center would be:

```python
rendition_obj = ImageRenditionType.create_from(
    attachment=original_image.image,
    filter_specs=["crop-50x50x100x100"]
)
```

### Do Nothing

This as it sounds does nothing to the image and is useful if you want to still create
the rendition but you do not want to change the image.

The format required for this is:

```python
f"original"
```

For example an image of 200x200 then you want to remain unchanged is:

```python
rendition_obj = ImageRenditionType.create_from(
    attachment=original_image.image,
    filter_specs=["original"]
)
```

### Fill

Resize and crop to fill the exact dimensions specified.

This can be particularly useful for websites requiring square thumbnails of arbitrary images. 
For example, a landscape image of width 2000 and height 1000 treated with the 
fill200x200 rule would have its height reduced to 200, 
then its width (ordinarily 400) cropped to 200.

This resize-rule will crop to the image’s focal point if it has been set. 
If not, it will crop to the centre of the image..

The format required for this is:

```python
f"fill-{width}x{height}"
```

#### On images that won’t upscale

It’s possible to request an image with fill dimensions that the image can’t 
support without upscaling. e.g. an image of width 400 and height 200 requested 
with fill-400x400. In this situation the ratio of the requested fill will be matched, 
but the dimension will not. So that example 400x200 image (a 2:1 ratio) could become 
200x200 (a 1:1 ratio, matching the resize-rule).

For example an image of 200x200 then you want to fill a 200x100 space is:

```python
rendition_obj = ImageRenditionType.create_from(
    attachment=original_image.image,
    filter_specs=["fill-200x100"]
)
```

#### Cropping closer to the focal point

By default, we will only crop enough to change the aspect ratio of the image to match the ratio in the resize-rule.

In some cases (e.g. thumbnails), it may be preferable to crop closer to the focal point, so that the subject of the image is more prominent.

You can do this by appending `-c<percentage>` at the end of the resize-rule. For example, if you would like the image to be cropped as closely as possible to its focal point, add `-c100`:

```python
f"fill-{width}x{height}-c100"
```

This will crop the image as much as it can, without cropping into the focal point.

If you find that -c100 is too close, you can try `-c75` or `-c50`. Any whole number from 0 to 100 is accepted.

### Format

This is an operation that will change the format of the file. You can only use either
`jpeg` or `png`.

The format required for this is:

```python
f"format-{format}"
```

For example an image of `png` then you want to save as a `jpeg` is:

```python
rendition_obj = ImageRenditionType.create_from(
    attachment=original_image.image,
    filter_specs=["format-jpeg"]
)
```

### Min and Max

`[min]`

This is to basically cover the given dimensions.

This may result in an image slightly larger than the dimensions you specify. 
A square image of width 2000 and height 2000, treated with the min-500x200 operation 
would have its height and width changed to 500,
i.e matching the width of the resize-rule, but greater than the height.

The format required for this is:

```python
f"min-{width}x{height}"
```

`[max]`

Fit within the given dimensions.

The longest edge will be reduced to the matching dimension specified.
For example, a portrait image of width 1000 and height 2000, 
treated with the max-1000x500 rule (a landscape layout) would result in the image 
being shrunk so the height was 500 pixels and the width was 250.

The format required for this is:

```python
f"max-{width}x{height}"
```

### Scale

The scale operation reduces the image in size by the percentage specified.

The format required for this is:

```python
f"scale-{percent}"
```

For example an image of 200x100 that you scale to 50 would end up 100x50:

```python
rendition_obj = ImageRenditionType.create_from(
    attachment=original_image.image,
    filter_specs=["scale-50"]
)
```

### Width and Height

`[width]`

Reduces the width of the image to the dimension specified.

The format required for this is:

```python
f"width-{width}"
```

`[height]`

Reduces the height of the image to the dimension specified.

The format required for this is:

```python
f"height-{height}"
```
