# -*- coding: utf-8 -*-
# @Author  : Zijian li
# @Time    : 2023/5/6 12:49

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from api.build_pinecone import init_pinecone
from api.qa import retrieve, complete, chat_complete
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Define a message model to be used in the API
class Message(BaseModel):
    message: str


index = init_pinecone()


@app.post('/api/chat')
async def chat(request: Request, message: Message):
    # Get the user's message from the request
    query = message.message
    # get prompt from query and pinecone
    prompt = retrieve(query, index)
    # get response
    response = chat_complete(prompt)['content']

    # convert unicode content to utf-8
    res_json = json.dumps(response, ensure_ascii=False)

    # 去掉res_json两侧的引号
    res_json = res_json[1:-1]

    return JSONResponse({'response': res_json})


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=9090)
