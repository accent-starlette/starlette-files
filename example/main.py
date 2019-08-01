import jinja2
import os
import uvicorn
import sqlalchemy as sa
import typing

from sqlalchemy import orm
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.staticfiles import StaticFiles
from starlette_core.database import Base, Database, Session
from starlette_core.templating import Jinja2Templates

from starlette_files.constants import MB
from starlette_files.fields import ImageAttachment, ImageRenditionAttachment
from starlette_files.storages import FileSystemStorage

root_directory = "/tmp/starlette"
dir_path = os.path.dirname(os.path.realpath(__file__))
templates_path = os.path.join(dir_path, "templates")


class MyImage(ImageAttachment):
    storage = FileSystemStorage(root_directory)
    directory = "images"
    allowed_content_types = ["image/jpeg", "image/png"]
    max_length = MB * 5


class MyImageRendition(ImageRenditionAttachment):
    storage = FileSystemStorage(root_directory)
    directory = "image-renditions"


class MyImageModel(Base):
    file = sa.Column(MyImage.as_mutable(sa.JSON))
    renditions = orm.relationship("MyImageRenditionModel")

    def get_rendition(self, filter_specs: typing.List[str]) -> "MyImageRenditionModel":
        rendition = MyImageRenditionModel.query.filter(
            MyImageRenditionModel.image_id==self.id,
            MyImageRenditionModel.filter_spec=="-".join(filter_specs),
            MyImageRenditionModel.file["cache_key"]==self.file.cache_key,
        ).one_or_none()

        if rendition:
            return rendition

        rendition = MyImageRenditionModel(
            image_id=self.id,
            file=MyImageRendition.create_from(self.file, filter_specs),
            filter_spec="-".join(filter_specs),
        )

        session = sa.inspect(self).session
        session.add(rendition)
        session.commit()

        return rendition


class MyImageRenditionModel(Base):
    file = sa.Column(MyImageRendition.as_mutable(sa.JSON))
    image_id = sa.Column(sa.Integer, sa.ForeignKey("myimagemodel.id"), nullable=False)
    image = orm.relationship("MyImageModel")
    filter_spec = sa.Column(sa.Text)


db = Database("sqlite:///")
db.create_all()

app = Starlette(debug=True)
app.mount("/fs", StaticFiles(directory=root_directory, check_dir=False), name="fs")

templates = Jinja2Templates(loader=jinja2.FileSystemLoader(templates_path))

@app.route("/")
class Homepage(HTTPEndpoint):
    async def get(self, request):
        return templates.TemplateResponse("home.html", {"request": request})

    async def post(self, request):
        form = await request.form()

        saved_file = MyImage.create_from(form["file"].file, form["file"].filename)
        image = MyImageModel(file=saved_file)
        image.save()
        
        return templates.TemplateResponse("image.html", {"request": request, "image": image})
