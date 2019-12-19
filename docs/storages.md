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

Awaiting docs.