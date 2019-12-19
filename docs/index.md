# Introduction

This package's primary purpose is for handling files and the storage of those files.
It uses SQLAlchemy as it's method of storing a reference to where those files
are located within the given storage.

There are currently two different types of storage. Amazon's S3 Simple Storage and a local file system storage.

In addition to this there is additional functionality when dealing specifically with images.
This includes operations such as resizing, cropping and changing the file format. This is without 
changing the original file.

## Getting Started - Installation

This package has not been published to [PyPI](https://pypi.org) so you will need to install it from
this [repo](https://github.com/accent-starlette/starlette-files). To do this simply run:

```
pip install git+https://github.com/accent-starlette/starlette-files.git@master#egg=starlette-files
```

The minimum Python requirement is 3.7.