import platform
import sys

import fastapi
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

import config
from backend import mount_backend

config.read_config()

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mount_backend(app)

@app.get("/ui", response_class=HTMLResponse)
async def dick():
    return open("web/webUI.html", "rb").read()

if __name__ == '__main__':
    if sys.version_info != (3,9) and platform.system() != "Linux":
        sys.exit("You must use Python 3.9 and Linux")

    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)