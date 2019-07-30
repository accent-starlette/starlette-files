import typing
import urllib
from io import BytesIO

from ..constants import KB
from ..exceptions import MissingDependencyError
from .base import Storage

# Importing optional stuff required by S3 store
try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None


class S3Storage(Storage):
    def __init__(
        self,
        bucket: str,
        access_key: str,
        secret_key: str,
        region: str,
        max_age: int = 60 * 60 * 24 * 365,
        prefix: str = None,
        endpoint_url: str = None,
        acl: str = "private",
    ) -> None:
        if boto3 is None:  # pragma: no cover
            raise MissingDependencyError(
                "boto3 must be installed to use the 'S3Storage' class."
            )

        self.session = boto3.session.Session()
        self.config = boto3.session.Config(
            s3={"addressing_style": "path"}, signature_version="s3v4"
        )

        self.endpoint_url = endpoint_url

        self.s3 = self.session.resource(
            "s3",
            config=self.config,
            endpoint_url=self.endpoint_url,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        self.bucket = self.s3.Bucket(bucket)
        self.max_age = max_age
        self.prefix = prefix
        self.acl = acl

    def get_s3_path(self, filename: str):
        if self.prefix:
            return "{0}/{1}".format(self.prefix, filename)
        return filename

    def _upload_file(
        self, filename: str, data: str, content_type: str, rrs: bool = False
    ):
        return self.bucket.put_object(
            Key=filename,
            Body=data,
            ACL=self.acl,
            CacheControl="max-age=" + str(self.max_age),
            StorageClass="REDUCED_REDUNDANCY" if rrs else "STANDARD",
            ContentType=content_type or "",
        )

    def put(self, filename: str, stream: typing.IO) -> int:
        path = self.get_s3_path(filename)
        stream.seek(0)
        data = stream.read()
        content_type = getattr(stream, "content_type", None)
        rrs = getattr(stream, "reproducible", False)
        self._upload_file(path, data, content_type, rrs=rrs)
        return len(data)

    def delete(self, filename: str) -> None:
        path = self.get_s3_path(filename)
        self.bucket.Object(path).delete()

    def open(self, filename: str, mode: str = "rb") -> typing.IO:
        path = self.get_s3_path(filename)
        obj = self.bucket.Object(path).get()
        return BytesIO(obj["Body"].read())

    def _strip_signing_parameters(self, url):
        split_url = urllib.parse.urlsplit(url)
        qs = urllib.parse.parse_qsl(split_url.query, keep_blank_values=True)
        blacklist = {
            "x-amz-algorithm",
            "x-amz-credential",
            "x-amz-date",
            "x-amz-expires",
            "x-amz-signedheaders",
            "x-amz-signature",
            "x-amz-security-token",
            "awsaccesskeyid",
            "expires",
            "signature",
        }
        filtered_qs = ((key, val) for key, val in qs if key.lower() not in blacklist)
        joined_qs = ("=".join(keyval) for keyval in filtered_qs)
        split_url = split_url._replace(query="&".join(joined_qs))
        return split_url.geturl()

    def locate(self, filename) -> str:
        path = self.get_s3_path(filename)
        params = {"Key": path, "Bucket": self.bucket.name}
        expires = 3600

        url = self.bucket.meta.client.generate_presigned_url(
            "get_object", Params=params, ExpiresIn=expires
        )

        if self.acl in ["public-read", "public-read-write"]:
            url = self._strip_signing_parameters(url)

        return url
