import sqlalchemy as sa
import uvicorn
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette_core.database import Base, Database, Session

from starlette_files.constants import MB
from starlette_files.fields import ImageAttachment
from starlette_files.storages import FileSystemStorage

root_directory = "/tmp/starlette"


class MyImage(ImageAttachment):
    storage = FileSystemStorage(root_directory)
    directory = "images"
    allowed_content_types = ["image/jpeg", "image/png"]
    max_length = MB * 2


class MyImageModel(Base):
    file = sa.Column(MyImage.as_mutable(sa.JSON))


db = Database("sqlite:///")
db.create_all()

app = Starlette(debug=True)
app.mount("/fs", StaticFiles(directory=root_directory, check_dir=False), name="fs")

@app.route("/")
class Homepage(HTTPEndpoint):
    async def get(self, request):
        html = """
        <html>
        <head></head>
        <body>
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <input type="submit" value="Submit">
            </form>
        </body>
        </html>
        """
        return HTMLResponse(html)

    async def post(self, request):
        form = await request.form()
        model = MyImageModel()
        model.file = await MyImage.create_from(form["file"].file, form["file"].filename)
        model.save()
        image_url = request.url_for("fs", path=model.file.path)
        html = f"""
        <html>
        <head></head>
        <body>
            <pre>{model.file}</pre>
            <img src="{image_url}" style="max-width:100%;">
            <p>{model.file.locate}</p>
            <a href="/">Again...</a>
        </body>
        </html>
        """
        return HTMLResponse(html)
