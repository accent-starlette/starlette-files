# Handling Files

Now you have decided on the storage its time to start saving files.

The first thing to do it to setup an attachment class. This is the SQLAlchemy
field that stores the info for your file including its location in the storage. It 
is also what interacts between the table and the storage to save and retrieve the files bytes.

```python
from starlette_files.constants import MB
from starlette_files.fields import FileAttachment

class FileType(FileAttachment):
    # your storage 
    storage = my_storage
    # directory in the stroage to save files to
    directory = "files"
    # allowed content types
    allowed_content_types = ["application/pdf"]
    # maximum allowed size in bytes
    max_length = MB * 5
```

!!! info "About content types"

    To determine if the content type is allowed we use a package called
    [python-magic](https://github.com/ahupp/python-magic). This identifies file types
    by checking their headers according to a predefined list of file types. This
    guards against the likes of someone renaming a .exe to a .pdf. This
    should be able to detect the file is infact an exe and will raise an exception
    if not valid.

    Please read their docs on installation as you will need additional os dependencies.

Next setup your table to include the field:

```python
import sqlalchemy as sa

class File(Base):
    file = sa.Column(FileType.as_mutable(sa.JSON))
```

## Saving Files

```python
async def post(request):
    form = await request.form()

    session = Session()
    file_obj = FileType.create_from(
        file=form["file"].file,
        original_filename=form["file"].filename
    )
    instance = File(file=file_obj)
    session.add(instance)
    session.commit()
    
    # return your response
```

An example form:

```html
<form method="post" enctype="multipart/form-data">
    <input type="file" name="file" required>
    <input type="submit" value="Submit">
</form>
```

## Working with Files

A `FileAttachment` is a `sqlalchemy.ext.mutable.MutableDict` and therefore stores
JSON as its value in the database. An example of this is:

```bash
>>> file = session(File).query.first()
>>> file.file
{
    'original_filename': 'example.pdf',
    'uploaded_on': 1576792678,
    'content_type': 'application/pdf',
    'extension': '.pdf',
    'file_size': 2897,
    'saved_filename': '9fabf09a-d915-48e5-8775-4f553c571a0b.pdf'
}
```

Each of the above has a property too so your can just do:

```bash
>>> file.file.original_filename
'example.pdf'
```

Additional properties include:

```python
@property
def path(self) -> str:
    """
    the path located within the storage

    if the directory on the FileAttachment is 'files' and the
    saved_filename is 'foo.txt' this will be 'files/foo.txt'
    """

@property
def locate(self) -> str:
    """
    this differs between storages and uses .path to get the file.
    using .path allows you to move the files to a different storage 
    and as long as they live in the same path the rest will work as usual.

    for the filesystem storage this is the full file path on the system
    ie: /storage-path/files/foo.txt

    for the s3 storage its the url to access the file
    ie: https://bucket.s3.....storage-path/files/foo.txt
    """

@property
def open(self) -> typing.IO:
    """
    opens the file
    
    with file.open as f:
        # do something with f
    """
```