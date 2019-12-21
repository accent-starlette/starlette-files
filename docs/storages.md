# Storages

Firstly you will need to decide what type of storage to use.

The storages primary function is to be able to `put`, `open`, `locate` and `delete` a file.

## File System Storage

The file system storage simply uses the local file system to store the files.
Firstly define the storage:

```python
from starlette_files.storages import FileSystemStorage

my_storage = FileSystemStorage(root_path="/path-to-storage")
```

## S3 Storage

The S3 storage uses an amazon S3 bucket to store its files. You will need an Amazon 
account and there is an additional fee to using the S3 service.
For more details see [here](https://aws.amazon.com/s3/).

You will need an IAM account that has access to your bucket.

!!! info "Using the `S3Storage`"

    An additional package is required when using S3 called [boto3](https://github.com/boto/boto3).
    to include this run:

    ```pip install git+https://github.com/accent-starlette/starlette-files.git@master#egg=starlette-files[s3]```

Once you have all this define the storage:

```python
from starlette_files.storages import S3Storage

my_storage = S3Storage(
    bucket="your-bucket-name",
    access_key="your-access-key",
    secret_key="your-secret-access-key",
    # region: the location of your bucket, i.e. eu-west-2
    region="aws-region",
    # acl: whether the files should remain private, public-read etc
    # for further info see:
    # https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl
    # the default is private
    acl="public-read",
    # prefix: the root path of the storage ie "/path-to-storage"
    # default is None for the root of the bucket
    prefix=None,
)
```

## Rolling Your Own

If your need to define your own storage your class should inherit from
`starlette_files.storages.Storage`. The only defined methods can be seen below and
all will need implementing:

```python
class Storage:
    """ The abstract base class for all stores. """

    def put(self, filename: str, stream: typing.IO) -> int:
        """
        Should be overridden in inherited class and puts the file-like object
        as the given filename in the store.

        :param filename: the target filename.
        :param stream: the source file-like object
        :return: length of the stored file.
        """
        raise NotImplementedError()

    def delete(self, filename: str) -> None:
        """
        Should be overridden in inherited class and deletes the given file.

        :param filename: The filename to delete
        """
        raise NotImplementedError()

    def open(self, filename: str, mode: str = "rb") -> typing.IO:
        """
        Should be overridden in inherited class and return a file-like object
        representing the file in the store.
        :param filename: The filename to open.
        :param mode: same as the `mode` in famous :func:`.open` function.
        """
        raise NotImplementedError()

    def locate(self, filename: str) -> str:
        """
        If overridden in the inherited class, should locate the file's url
        to share in public space or a path of some sort to locate it.

        This method is not used internally by starlette-files it is just a 
        handy helper that gets returned by an Attachment property.

        :param filename: The filename to locate.
        """
        raise NotImplementedError()
```