# Handling Images

The basics of handling images is the same as handling files. The only difference is
that you will need to inherit from `ImageAttachment` instead of `FileAttachment`.

!!! info "Using the `ImageAttachment`"

    An additional package is required when using images called [pillow](https://pypi.org/project/Pillow/).
    to include this run:

    ```pip install git+https://github.com/accent-starlette/starlette-files.git@master#egg=starlette-files[image]```

```python
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
```

And define your table:

```python
import sqlalchemy as sa

class Image(Base):
    image = sa.Column(ImageType.as_mutable(sa.JSON))
```

## Working with Images

The only difference here is that it saves two additional bits of data,
the width and the height of the image:

```bash
>>> instance = session.query(Image).first()
>>> instance.image
{
    'original_filename': 'example.png',
    'uploaded_on': 1576792678,
    'content_type': 'image/png',
    'extension': '.png',
    'file_size': 2897,
    'saved_filename': '9fabf09a-d915-48e5-8775-4f553c571a0b.png',
    'width': 800,
    'height': 600,
}
```

These both also include properties:

```bash
>>> instance.image.width
800
```

## Focal Point

On an `ImageAttachment` you can also specify a focal point. This is the area of
the image that is most important. 

To set this you can do:

```bash
>>> instance.image.focal_point_x = 100  # px from the left 
>>> instance.image.focal_point_y = 100  # px from the top
>>> instance.image.focal_point_width = 100  # width
>>> instance.image.focal_point_height = 100  # height
```

This is useful when dealing with [image operations](../image_operations) such as the
[fill operation](../image_operations#fill).