import sqlalchemy as sa
import uvicorn
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse
from starlette_core.database import Base, Database, Session

from starlette_files.constants import MB
from starlette_files.fields import FileAttachment
from starlette_files.middleware import LimitUploadSize
from starlette_files.storages import FileSystemStorage


class MyFS(FileAttachment):
    storage = FileSystemStorage("/tmp/starlette")
    directory = "files"
    allowed_content_type = ["image/jpeg", "image/png"]


class MyModel(Base):
    file = sa.Column(MyFS.as_mutable(sa.JSON))


db = Database("sqlite:///")
db.create_all()

app = Starlette(debug=True)

app.add_middleware(LimitUploadSize, max_upload_size=MB * 5)


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
        model = MyModel()
        model.file = await MyFS.create_from(form["file"].file, form["file"].filename)
        model.save()
        html = f"""
        <html>
        <head></head>
        <body>
            <pre>{model.file}</pre>
            <p>{model.file.locate}</p>
            <a href="/">Again...</a>
        </body>
        </html>
        """
        return HTMLResponse(html)
