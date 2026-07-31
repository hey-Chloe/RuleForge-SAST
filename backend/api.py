from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import shutil
import os

from engine.semgrep_runner import scan


app = FastAPI()



# 解决 Vue(localhost:5173)
# 请求 FastAPI(127.0.0.1:8000) 的跨域问题

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)



@app.post("/scan")
async def scan_code(
    file: UploadFile = File(...)
):


    # 保存上传文件

    path = "temp.php"


    with open(path, "wb") as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    # 调用 Semgrep 扫描

    result = scan(

        path,

        "../rules/php-unserialize.yaml"

    )



    # 删除临时文件

    if os.path.exists(path):

        os.remove(path)



    return result